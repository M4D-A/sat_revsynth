#include "circuit.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

bool Circuit::isSuper(const Circuit &rhs) const {
  if (rhs.width != width)
    throw std::runtime_error("Width mismatch");

  if (rhs.gc > gc)
    throw std::runtime_error("GC mismatcht");

  // Check if rhs literals is a sublist of self literals
  if (rhs.literals.empty())
    return true;

  auto it = std::search(literals.begin(), literals.end(), rhs.literals.begin(),
                        rhs.literals.end());

  return it != literals.end();
}

bool Circuit::isReducible(const std::vector<Circuit> &structures) const {
  for (const auto &structure : structures) {
    try {
      if (isSuper(structure)) {
        return true;
      }
    } catch (const std::runtime_error &e) {
      // Ignore width and depth mismatch errors
    }
  }
  return false;
}

bool Circuit::operator<(const Circuit &rhs) {
  if (width != rhs.width)
    return width < rhs.width;
  if (gc != rhs.gc)
    return gc < rhs.gc;
  return literals < rhs.literals;
}

bool Circuit::operator==(const Circuit &rhs) {
  return width == rhs.width && gc == rhs.gc && literals == rhs.literals;
}

void Circuit::print() const {
  std::cout << "Width: " << width << ", Depth: " << gc << std::endl;
  for (const auto &row : literals) {
    for (int literal : row) {
      std::cout << literal << " ";
    }
    std::cout << std::endl;
  }
}

Collection::Collection(const std::string &filename) {
  std::ifstream file(filename);
  if (!file) {
    throw std::runtime_error("Failed to open file");
  }

  std::string line;
  while (std::getline(file, line)) {
    if (line.empty()) {
      continue;
    }

    if (line[0] == 'h') {
      std::istringstream iss(line.substr(2));
      iss >> max_width >> max_gc;
      circuits.resize(max_width + 1,
                      std::vector<std::vector<Circuit>>(max_gc + 1));
    } else if (line[0] == 'c') {
      std::istringstream iss(line.substr(2));
      Circuit circuit;
      iss >> circuit.width >> circuit.gc;

      std::string literalLine;
      while (std::getline(file, literalLine) && !literalLine.empty()) {
        std::istringstream lss(literalLine);
        std::vector<int> row;
        int literal;
        while (lss >> literal) {
          row.push_back(literal);
        }
        circuit.literals.push_back(row);
      }

      circuits[circuit.width][circuit.gc].push_back(circuit);
    }
  }
}

void Collection::print() const {
  for (size_t width = 0; width < circuits.size(); ++width) {
    auto &width_subcoll = circuits[width];
    for (size_t gc = 0; gc < width_subcoll.size(); ++gc) {
      auto len = width_subcoll[gc].size();
      std::cout << "(" << width << ", " << gc << "): " << len << std::endl;
    }
  }
}

void rmReducible(std::vector<Circuit> &lhs, const std::vector<Circuit> &rhs) {
  auto it = lhs.begin();
  while (it != lhs.end()) {
    bool isReducible = false;

    for (const auto &rhsStructure : rhs) {
      try {
        if (it->isSuper(rhsStructure)) {
          isReducible = true;
          break;
        }
      } catch (const std::runtime_error &e) {
        // Ignore width and depth mismatch errors
      }
    }

    if (isReducible) {
      it = lhs.erase(it);
    } else {
      ++it;
    }
  }
}

void rmDuplicates(std::vector<Circuit> &structures) {
  std::sort(structures.begin(), structures.end());
  structures.erase(std::unique(structures.begin(), structures.end()));
}

void rmReducible(Collection &collection) {
  int max_width = collection.max_width;
  int max_gc = collection.max_gc;
  for (int width = 0; width <= max_width; width++) {
    for (int red_gc = 0; red_gc <= max_gc; red_gc++) {
      const auto &red_dg = collection.circuits[width][red_gc];
      for (int target_gc = red_gc + 1; target_gc <= max_gc; target_gc++) {
        auto &target_dg = collection.circuits[width][target_gc];
        rmReducible(target_dg, red_dg);
      }
    }
  }
}

// def remove_reducibles(self) -> "Collection":
//     for width, reducing_gc in copy(self._group_ids_iter):
//         print(f"  -- RMD({width}, {reducing_gc})")
//         reducing_dg = self[width][reducing_gc]
//         for reducted_gc in range(reducing_gc + 1, self._max_gate_count +
//         1):
//             reducted_dg = self[width][reducted_gc]
//             reducted_dg.remove_reducibles(reducing_dg)
//     return self
