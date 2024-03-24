#include <string>
#include <vector>

struct Circuit {
  int width;
  int gc;
  std::vector<std::vector<int>> literals;

  bool isSuper(const Circuit &rhs) const;
  bool isReducible(const std::vector<Circuit> &structures) const;
  bool operator<(const Circuit &rhs);
  bool operator==(const Circuit &rhs);

  void print() const;
};

struct Collection {
  int max_width;
  int max_gc;
  std::vector<std::vector<std::vector<Circuit>>> circuits;

  Collection(const std::string &filename);
  void print() const;
  void dump(const std::string &filename);
};

std::vector<Circuit> nonReducible(const std::vector<Circuit> &lhs,
                                  const std::vector<Circuit> &rhs);

void rmDuplicates(std::vector<Circuit> &structures);

void rmReducible(Collection &collection);

void rmDuplicates(Collection &collection);
