#include "circuit.hpp"
#include <string>

int main() {
  std::string filename = "/home/adam/dump_3_7.txt";
  printf("Reading ...");
  Collection coll(filename);
  printf("Done\n");
  rmReducible(coll);
  coll.print();

  return 0;
}
