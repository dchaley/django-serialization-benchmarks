# Django Serialization Benchmarks

This project benchmarks various Django serialization methods, including Django REST Framework (DRF), Django Ninja, and Strawberry GraphQL.

## Prerequisites

- Python 3.11 or higher

## Installation

To set up the project environment and install dependencies using a virtual environment (`.venv`), follow these steps:

1. **Create the virtual environment:**

   ```bash
   python3.11 -m venv .venv
   ```

2. **Activate the virtual environment:**

   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows (Command Prompt):
     ```cmd
     .venv\Scripts\activate
     ```

3. **Install the dependencies:**

   Install the dependencies directly from `pyproject.toml` using `pip`:

   ```bash
   pip install .
   ```

## Running Benchmarks

To run the full suite of benchmarks and generate charts:

```bash
bash benchmark.sh
```

The results and generated charts will be saved in the `results/` directory.
