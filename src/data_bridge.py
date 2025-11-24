# This module provides boilerplate code for reading/writing JSON in C++, Rust, Go, Java.
# In a real system, this would generate code that uses libraries (serde, jackson, etc.)
# For this demo, we will use simple file IO with manual parsing or assumption of format.

class DataBridge:
    @staticmethod
    def get_read_code(lang, var_name, var_type):
        """
        Generates code to read 'data.json' and extract a value.
        Simplification: We assume data.json contains just the value or a simple dict {"value": ...}
        """
        if lang == "Rust":
            return f"""
    // Mock Data Read
    let {var_name}: {var_type} = 50; // In real system: read_json("data.json")
"""
        elif lang == "C++":
            return f"""
    // Mock Data Read
    {var_type} {var_name} = 50; // In real system: read_json("data.json")
"""
        # ... implement others if needed
        return ""

    @staticmethod
    def get_write_code(lang, var_name):
        """
        Generates code to write result to 'data_out.json'.
        """
        if lang == "Rust":
            return f'    std::fs::write("data_out.json", format!("{{}}", {var_name})).expect("Unable to write file");'
        elif lang == "C++":
            return f'    ofstream outfile("data_out.json"); outfile << {var_name}; outfile.close();'
        elif lang == "Go":
            return f'    ioutil.WriteFile("data_out.json", []byte(fmt.Sprintf("%v", {var_name})), 0644)'
        elif lang == "Java":
            return f'    try {{ Files.write(Paths.get("data_out.json"), String.valueOf({var_name}).getBytes()); }} catch (IOException e) {{}}'
        return ""
