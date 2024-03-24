class Doughnut {
  cook() {
    echo "Fry until golden brown.";
    echo "Place in a nice box.";
  }
}

class BostonCream<Doughnut> {
  test() {
    super::cook();
  }
}

BostonCream().cook();
BostonCream().test();


// list is a PloxClass with predefine methods
// Behaves like stack
// List Class has to hold some fields like:
// len, capacity, etc..
// 
// let a = []
// a.push();     // push top
// a.pop();      // pop top
// a.remove(1);  // remove by index
// a.append(3);  // append by index
// a.sort();     // simple sort
// a.rand();     // get random element
