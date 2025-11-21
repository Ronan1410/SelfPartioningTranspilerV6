// Transpiled to Rust
fn collatz_sequence_sum() -> i32 {
    let mut total_steps = 0;
    for i in 1..51 {
        let mut n = i;
        let mut steps = 0;
        while n != 1 {
            if (n % 2) == 0 {
                n = (n / 2) as i32;
            } else {
                n = ((3 * n) + 1);
            }
            steps += 1;
        }
        total_steps += steps;
    }
    return total_steps;
}

fn main() {
    println!("Collatz Sum: {}", collatz_sequence_sum());
}