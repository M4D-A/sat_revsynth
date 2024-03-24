#include "circuit.hpp"
#include <string>

int main() {
  std::string filename = "/home/adam/clean_data/unfexc_3_7.txt";
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
  coll.dump("/home/adam/clean_data/exc_3_7_cpp.txt");

  return 0;
}
