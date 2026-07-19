from pipeline import PipelineRunner

def main():
    # Cukup memanggil SATU fungsi utama dari pipeline master
    orchestrator = PipelineRunner()
    final_output = orchestrator.run_all_pipelines()
    print(final_output)

if __name__ == "__main__":
    main()