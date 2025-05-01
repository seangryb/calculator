# SymCal Graph - Symbolic Graphing Calculator

SymCal Graph is a desktop symbolic calculator application with interactive plotting capabilities built on the Python libraries: PySide6, Matplotlib, and SymPy. It allows users to evaluate mathematical expressions, perform symbolic calculus operations (differentiation, integration), solve algebraic and differential equations, compute Fourier transforms and visualise functions interactively with varying parameters. In short, any computations that SymPy can do, SymCal Graph can do as well with fast, interactive plots of the results.

The app is designed for users who want fast symbolic calculations and visualisations but don't want to worry too much about syntax or have time to write or run a full Python/Matlab/Mathematica script.

## Features

*   **Expression Evaluation:** Evaluate standard mathematical expressions.
*   **Interactive Plotting:** Plot functions, (`f(x)`), of a single variable interactively with variable parameter values and export them as PDFs.
*   **Symbolic Calculus:**
    *   Calculate symbolic derivatives (`f'(x)`).
    *   Calculate symbolic indefinite integrals (`∫f(x)dx`).
*   **Equation Solving:** Find symbolic solutions for `f(x) = 0`.
*   **Direct SymPy Commands:** Execute arbitrary SymPy commands for advanced operations including Fourier transform computation as well as ODE and PDE solving. 

## Screenshot

![Screeshot](/examples/Screenshot%20(wavepacket).png)

## Installation

#### macOS
1. Download the `SymCal Graph.dmg` file from the [dist directory](https://github.com/seangryb/calculator/blob/main/dist/).
2. Open the `.dmg` file and drag the SymCal Graph app to your Applications folder.
3. Launch the app from the Applications folder.

#### Windows
1. Download the `SymCal Graph.zip` file containing the required files from the [dist directory](https://github.com/seangryb/calculator/blob/main/dist/).
2. Extract the contents of the `.zip` file to a folder of your choice.
3. Run the `SymCalGraph.exe` file directly to start the application.

*This app has not been tested on Windows.*

#### Running from Source
1. Ensure Python 3.8+ is installed on your system.
2. Install the required dependencies by running:
    ```bash
    pip install -r requirements.txt
    ```
3. Navigate to the project directory and run the app using:
    ```bash
    python main.py
    ```

## Usage

1.  **Evaluate Expression:** Enter a mathematical expression (e.g., `2 * pi`, `sqrt(10)`) in the "Expression" field and click "Evaluate" or press Enter.
2.  **Function Operations:**
    *   Enter a function of `x` with arbitrary parameters (e.g., `(x-a)**3 - b*sin(x)`) in the "Function f(x)" field.
    *   Click the derivative, integral, or solve buttons to perform the respective operations symbolically.
    *   Click "Plot" to graph the function. Free parameters can be interactively adjusted using slider bars (with default value `1` and an adjustable range with default `(-10, 10)`). Customize plot options (range, labels, title) in the "Plotting Options" and click "Plot" to refresh. For complex functions, select options to plot real (Re) or imaginary (Im) as well as the absolute value (Abs) or phase (Arg).
3.  **Run Command:** Enter a valid SymPy command (e.g., `limit(sin(a*x)/x, x, 0)`) in the "Input Command" field and click "Run Command" or press Enter. This can be any SymPy command.
4.  **Copy Output:** Click "Copy Last Output" (Ctrl+Shift+C) to copy the numerical or symbolic result from the last operation.
5.  **Save Plot:** Use the "Plot" menu -> "Save as PDF" (Ctrl+S) to save the current graph.

Expressions should follow SymPy syntax. (No need to define symbols for variables or parameters: SymCal Graph will do that automatically!) See the [SymPy Tutorials](https://docs.sympy.org/latest/tutorials/intro-tutorial/features.html) or the [SymPy API](https://docs.sympy.org/latest/reference/public/basics/index.html#basic-modules) for a list all the available operations and protected symbols (eg, `I = \sqrt(-1)`, `pi`, etc).

