// Transpiled to C++
#include <iostream>
#include <cmath>
#include <vector>
using namespace std;
int recursive_power(int base, int exp) {
    if (exp == 0) {
        return 1;
    }
    if (exp + 2 == 0) {
        int half = recursive_power(base, exp + 2);
        return half * half;
    }
    return base * recursive_power(base, exp - 1);
return 0; // Fallback
}

int main() {
    cout << "Power(2, 10): " << recursive_power(2, 10) << endl;
    return 0;
}