import click
import os
import sys

# Add current directory to path to ensure imports work
sys.path.append(os.getcwd())

from src.parser import CodeParser
from src.splitter import SplitterOrchestrator
from src.transpiler import Transpiler, ExecutionWrapper
from visuals.graph import GraphGenerator
from visuals.report import ReportGenerator
from visuals.metadata import MetadataGenerator
from visuals.live import LiveVisualizer

@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output-dir', default='viz', help='Directory to save visualizations')
@click.option('--live-viz', is_flag=True, help='Show live parsing/lexing visualization')
@click.option('--execute', is_flag=True, help='Execute the transpiled code immediately')
def process(input_file, output_dir, live_viz, execute):
    """
    SelfPartitioningTranspilerV5 CLI.
    
    Parses a Python file, splits it using various strategies, and generates visualizations.
    """
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, 'r', encoding='utf-8') as f:
        source_code = f.read()

    if live_viz:
        try:
            viz = LiveVisualizer()
            viz.visualize_process(source_code)
        except ImportError:
            click.echo("Install 'rich' to see live visualizations.")
        except Exception as e:
            click.echo(f"Live visualization error: {e}")

    click.echo(f"Processing {input_file}...")

    # 1. Parse
    parser = CodeParser()
    parsed_module = parser.parse_source(source_code, input_file)
    click.echo(f"Parsed {len(parsed_module.segments)} initial segments.")

    # 2. Split & Balance
    splitter = SplitterOrchestrator()
    processed_module = splitter.process_module(parsed_module)
    click.echo(f"After splitting and balancing: {len(processed_module.segments)} segments.")

    # 3. Transpile
    click.echo("Transpiling and instrumenting code...")
    transpiler = Transpiler(output_dir)
    transpiled_path = transpiler.transpile(processed_module)
    transpiled_filename = os.path.basename(transpiled_path)

    wrapper = ExecutionWrapper(output_dir)
    wrapper.create_runner(transpiled_filename)

    # 4. Visualize
    click.echo("Generating static visualizations...")
    
    try:
        graph_gen = GraphGenerator(output_dir)
        graph_gen.generate(processed_module)
    except Exception as e:
        click.echo(f"Graph generation failed (Graphviz installed?): {e}")

    report_gen = ReportGenerator(output_dir)
    report_gen.generate(processed_module)

    meta_gen = MetadataGenerator(output_dir)
    meta_gen.generate(processed_module)

    click.echo("Done! Check the 'viz/' folder.")
    
    if execute:
        click.echo("\n--- Running Transpiled Code ---")
        # Execute the runner
        runner_path = os.path.join(output_dir, "run_transpiled.py")
        os.system(f"{sys.executable} {runner_path}")

if __name__ == '__main__':
    process()
