// Transpiled to Go
package main
import "fmt"
import "time"

func log_processor_pipeline() {
    fmt.Println("Init Pipeline")
    for i := 0; i < 3; i++ {
        time.Sleep(time.Duration(float64(time.Second) * 0.1))
        data_id := i + 100
        _ = data_id
        fmt.Printf("Processed Batch %v ID: %v\n", i, data_id)
    }
    fmt.Println("Pipeline Close")
}

func main() {
    log_processor_pipeline()
}