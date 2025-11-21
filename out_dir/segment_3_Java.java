// Transpiled to Java
public class Main {
    static class BankAccount {
        String id;
        int quantity;
        String name;
        int balance;
        String status;
        String sku;
        public BankAccount(String id) {
            this.id = id;
            this.balance = 1000;
            this.status = "Active";
        }
        public String deposit(int amount) {
            this.balance += amount;
            return "Deposit: " + String.valueOf(amount) + " New Balance: " + String.valueOf(this.balance);
        }
        public String withdraw(int amount) {
            if (this.balance >= amount) {
                this.balance -= amount;
                return "Withdraw: " + String.valueOf(amount) + " Remaining: " + String.valueOf(this.balance);
            }
            return "Insufficient Funds";
        }
    }
    
    public static void main(String[] args) {
        System.out.println("Running Java Demo...");
        BankAccount acc = new BankAccount("ACC-123");
        System.out.println(acc.deposit(500));
        System.out.println(acc.withdraw(200));
    }
}