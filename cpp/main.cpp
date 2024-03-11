#include "circuit.hpp"
#include <string>

int main() {
  std::string filename = "/home/adam/dump_3_7.txt";
  printf("Reading...");
  Collection coll(filename);
  printf("Done\n");
  printf("RM Reducibles...");
  rmReducible(coll);
  printf("Done\n");
  printf("RM Duplicates...");
  rmDuplicates(coll);
  printf("Done\n");
  coll.print();

  return 0;
}
