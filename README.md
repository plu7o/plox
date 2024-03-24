# Plox

## Syntax

### Operators
```
// Logic operations

let a = 1 >= 2;     
let b = 3 <= 4;
let c = 5 == 6;     
let d = 7 != 8;     
let e = !(9 < 10);  // Logic negation

// Ternary

let foo = 1 + 1 == 2 ? true : false;

// Arithmetic operations

let x = 1 + 1;      
let x = 1 - 1;  
let y = -x;         // Negation
let z = ++y;        // Prefix incerement
let z = y++;        // Postfix incerement
let a += 1;         // assignment operators
let a -= 1;
let a *= 1;
let a /= 1;

```
---
### Variables
```
let a = 1;
echo a;
```
---
### Functions
```
fn foo(bar, baz) {
    return bar + baz;
}

foo(1, 3);
```
---
### Closures
```
fn outer() {
    let x = 1;
    fn inner() {
        print x;
    }
    return inner();
}

let foo = outer();
foo();
```
---
### Anonymous Function
```
let foo = fn (a, b) {
    return a + b;
};

echo foo(1, 2); // prints 3
```
---

### Class
```
class Animal {
    // Constructor
    init(species) {
        self.species = species;
    }

    // Methods
    getSpecies() {
        return self.species;
    }

    setSpecies(newSpecies) {
        self.species = newSpecies;
    }
}

let dog = Animal("Canis");
print dog.getSpecies();

```
---
### Inheritance
```
class Animal {
    // Constructor
    init(species) {
        self.species = species;
    }

    // Methods
    getSpecies() {
        return self.species;
    }

    setSpecies(newSpecies) {
        self.species = newSpecies;
    }
}

class Dog<Animal> {
    getSpecies() {
        echo "this dog belongs to " + super::get_species(); 
    }
    makeSound() {
        echo "baaawrk baawrk#!";
    }
}

let dog = Dog();
print dog.getSpecies();
dog.makeSound();
```
---
## improvements
*- prefix & postfix operators
*- assignment operators
*- ternary expressions
*- Better Error messages

## Builtins
*- Time
*- Io
*- Collections

