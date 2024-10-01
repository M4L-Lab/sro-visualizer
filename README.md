# SRO Visualizer

This project provides an interactive dashboard to visualize the Short Range Order (SRO) calculation results. It simplifies the process of analyzing and plotting SQS (Special Quasirandom Structures) data using `ASE`, `pandas`, and `Plotly`.

## Installation

Before you begin, make sure the following Python libraries are installed:

```bash
pip install ase pandas plotly
```

## How to Analyze SQS Data

Follow these steps to analyze your SQS data and generate the required JSON file:

1. Navigate to the folder where you executed the SQS run.

2. Run the `analyze_sqs.py` script:

   ```bash
   python analyze_sqs.py
   ```

3. Modify the values for `cutoff` and `scale` (lattice constant) within the script according to your specific system configuration.

4. After running the script, you will obtain a JSON file containing the analysis results.

## Visualize SQS Data

Once you have your JSON file, follow these instructions to visualize the SRO data:

1. Run the `sqs_plot.py` script:

   ```bash
   python sqs_plot.py
   ```

2. Open the link that appears in your terminal in your browser.

3. Upload the JSON file you generated from the SQS analysis to the dashboard.

4. When you're done, use `Ctrl + C` in your terminal to exit the server.

Enjoy visualizing your SRO data!

---

If you have any questions or run into issues, feel free to reach out for help!
