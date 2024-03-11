#include "circuit.hpp"
#include <string>

int main() {
  std::string filename = "/home/adam/dump.txt";
  Collection coll(filename);
  rmReducible(coll);
  coll.print();

  return 0;
}
