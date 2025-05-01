import sys, os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QFormLayout, QGroupBox, QTextEdit, QFileDialog,
    QCheckBox, QSlider
)
from PySide6.QtGui import QAction, QKeySequence, QIcon
from PySide6.QtCore import Qt, QSize
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from sympy import symbols, diff, integrate, solve, parse_expr, SympifyError, latex, lambdify
from history_line_edit import HistoryLineEdit

basedir = os.path.dirname(__file__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SymCal Graph")
        self.setGeometry(100, 100, 1100, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Left Panel: Input and Controls
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)

        # --- General Expression Input ---
        self.left_layout.addWidget(QLabel("Expression:"))
        self.general_expression_input = HistoryLineEdit()
        self.general_expression_input.setPlaceholderText("Enter math expression (e.g., 2+2, sin(pi/2))")
        self.general_expression_input.setObjectName("General Expression Input")
        self.left_layout.addWidget(self.general_expression_input)
        self.evaluate_button = QPushButton("Evaluate")
        self.evaluate_button.setToolTip("Evaluate the expression above (Return)")
        self.left_layout.addWidget(self.evaluate_button)

        # --- Function Input ---
        self.left_layout.addWidget(QLabel("Function f(x):"))
        self.function_input = HistoryLineEdit()
        self.function_input.setPlaceholderText("Enter function of x (e.g., x**2 + 1)")
        self.function_input.setObjectName("Function Input")
        self.left_layout.addWidget(self.function_input)

        # --- Function Buttons ---
        func_button_layout = QHBoxLayout()
        self.derivative_button = QPushButton()
        self.derivative_button.setIcon(QIcon(os.path.join(basedir,"icons/diff_icon.png")))
        self.derivative_button.setIconSize(QSize(24,24))
        self.derivative_button.setShortcut(QKeySequence("Ctrl+D"))
        self.derivative_button.setToolTip(f"Calculate derivative f'(x) ({self.derivative_button.shortcut().toString(QKeySequence.PortableText)})")
        self.integral_button = QPushButton()
        self.integral_button.setIcon(QIcon(os.path.join(basedir,"icons/int_icon.png")))
        self.integral_button.setIconSize(QSize(24,24))
        self.integral_button.setShortcut(QKeySequence("Ctrl+I"))
        self.integral_button.setToolTip(f"Calculate integral ∫f(x)dx ({self.integral_button.shortcut().toString(QKeySequence.PortableText)})")
        self.solve_button = QPushButton("Solve")
        self.solve_button.setIcon(QIcon(os.path.join(basedir,"icons/solve.svg")))
        self.solve_button.setIconSize(QSize(24,24))
        self.solve_button.setShortcut(QKeySequence("Ctrl+S"))
        self.solve_button.setIconSize(QSize(24,24))
        self.solve_button.setToolTip(f"Solve f(x) = 0 ({self.solve_button.shortcut().toString(QKeySequence.PortableText)})")
        self.plot_button = QPushButton("Plot")
        self.plot_button.setIcon(QIcon(os.path.join(basedir,"icons/plot.png")))
        self.plot_button.setIconSize(QSize(24,24))
        self.plot_button.setShortcut(QKeySequence("Ctrl+P"))
        self.plot_button.setToolTip(f"Plot y = f(x) ({self.plot_button.shortcut().toString(QKeySequence.PortableText)})")

        func_button_layout.addWidget(self.derivative_button)
        func_button_layout.addWidget(self.integral_button)
        func_button_layout.addWidget(self.solve_button)
        func_button_layout.addWidget(self.plot_button)
        self.left_layout.addLayout(func_button_layout)

        # --- Plotting Controls ---
        plot_group = QGroupBox("Plotting Options")
        self.plot_options_layout = QFormLayout(plot_group,formAlignment=Qt.AlignmentFlag.AlignLeft, fieldGrowthPolicy=QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.plot_x_min_input = QLineEdit("-10")
        self.plot_x_max_input = QLineEdit("10")
        self.plot_num_points_input = QLineEdit("500")
        self.plot_title_input = QLineEdit("") # Default to empty
        self.plot_title_input.setPlaceholderText("Leave empty for default title") # Add placeholder
        self.plot_x_label_input = QLineEdit("x")  # Add input for X-label
        self.plot_y_label_input = QLineEdit("")  # Add Y-label input
        self.plot_y_label_input.setPlaceholderText("Leave empty for default label (f(x))")  # Add placeholder
        self.plot_y_min_input = QLineEdit("") # Add Y Min input
        self.plot_y_min_input.setPlaceholderText("Optional: Auto") # Add placeholder
        self.plot_y_max_input = QLineEdit("") # Add Y Max input
        self.plot_y_max_input.setPlaceholderText("Optional: Auto") # Add placeholder

        # Add Checkboxes for complex components
        self.plot_real_check = QCheckBox("Re")
        self.plot_imag_check = QCheckBox("Im")
        self.plot_abs_check = QCheckBox("Abs")
        self.plot_arg_check = QCheckBox("Arg")
        self.plot_real_check.setChecked(True) # Default to Real checked

        # Store checkboxes in a list for easier handling
        self.plot_checkboxes = [
            self.plot_real_check, self.plot_imag_check,
            self.plot_abs_check, self.plot_arg_check
        ]

        # Create a horizontal layout for X range inputs
        x_range_layout = QHBoxLayout()
        x_range_layout.addWidget(QLabel("Min:"))
        x_range_layout.addWidget(self.plot_x_min_input)
        x_range_layout.addWidget(QLabel("Max:"))
        x_range_layout.addWidget(self.plot_x_max_input)

        # Create a horizontal layout for Y range inputs
        y_range_layout = QHBoxLayout()
        y_range_layout.addWidget(QLabel("Min:"))
        y_range_layout.addWidget(self.plot_y_min_input)
        y_range_layout.addWidget(QLabel("Max:"))
        y_range_layout.addWidget(self.plot_y_max_input)

        self.plot_options_layout.addRow("Title:", self.plot_title_input)
        self.plot_options_layout.addRow("X Label:", self.plot_x_label_input)
        self.plot_options_layout.addRow("Y Label:", self.plot_y_label_input)
        self.plot_options_layout.addRow("X Range:", x_range_layout) # Add the X range layout
        self.plot_options_layout.addRow("Y Range:", y_range_layout) # Add the Y range layout
        self.plot_options_layout.addRow("Num Points:", self.plot_num_points_input)
        # Add checkboxes to the layout
        checkbox_layout = QHBoxLayout() # Use a QHBoxLayout for checkboxes
        checkbox_layout.addWidget(self.plot_real_check)
        checkbox_layout.addWidget(self.plot_imag_check)
        checkbox_layout.addWidget(self.plot_abs_check)
        checkbox_layout.addWidget(self.plot_arg_check)
        self.plot_options_layout.addRow("Plot:", checkbox_layout) # Add the layout

        self.left_layout.addWidget(plot_group)

        # --- Command Input ---
        command_section_layout = QVBoxLayout()
        command_section_layout.addWidget(QLabel("Input Command:"))
        self.command_input = HistoryLineEdit()
        self.command_input.setPlaceholderText("Enter command (e.g., diff(x**2, x))")
        command_section_layout.addWidget(self.command_input)
        self.command_button = QPushButton("Run Command")
        self.command_button.setShortcut(QKeySequence('Ctrl+Return'))
        self.command_button.setToolTip(f"Run the SymPy command above ({self.command_button.shortcut().toString(QKeySequence.PortableText)})")
        command_section_layout.addWidget(self.command_button)
        self.left_layout.addLayout(command_section_layout)

        # --- Result/Output Area ---
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.left_layout.addWidget(QLabel("Result/Output:"))
        self.left_layout.addWidget(self.result_output, 1)

        # Add Copy Button
        self.copy_button = QPushButton("Copy Last Output")
        self.copy_button.setShortcut(QKeySequence("Ctrl+Shift+C"))
        self.copy_button.setToolTip(f"Copy the last result value to the clipboard ({self.copy_button.shortcut().toString(QKeySequence.PortableText)})")
        self.left_layout.addWidget(self.copy_button)  # Add button below output

        # Right Panel: Plot Area
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel) # This sets the main layout for the right panel
        # Initialize plot_layout without a parent widget. It will be added to right_layout.
        self.plot_layout = QVBoxLayout()
        self.right_layout.addLayout(self.plot_layout, 1) # Add plot_layout inside right_layout, give it stretch factor 1

        # Placeholder for the canvas
        self._canvas = None

        # --- Parameter Sliders (Moved to Right Panel) ---
        self.parameter_group = QGroupBox("Parameters")
        self.parameter_layout = QFormLayout(self.parameter_group, formAlignment=Qt.AlignmentFlag.AlignLeft, fieldGrowthPolicy=QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.right_layout.addWidget(self.parameter_group) # Add below plot layout
        self.parameter_group.setVisible(False) # Initially hidden
        self.parameter_sliders = {} # {symbol_name: slider}
        self.parameter_labels = {} # {symbol_name: label}
        self.parameter_min_inputs = {} # {symbol_name: QLineEdit}
        self.parameter_max_inputs = {} # {symbol_name: QLineEdit}
        self.current_plot_expr = None
        self.current_plot_x = None
        self.current_plot_params = {} # Store param symbols {name: symbol}

        # Add panels to main layout
        self.layout.addWidget(self.left_panel, 1)
        self.layout.addWidget(self.right_panel, 2)

        # Menu Bar for Plot Options
        self._create_menus()

        # Connect Signals
        self.evaluate_button.clicked.connect(self.evaluate_expression)
        self.general_expression_input.returnPressed.connect(self.evaluate_expression)
        self.derivative_button.clicked.connect(self.calculate_derivative)
        self.integral_button.clicked.connect(self.calculate_integral)
        self.solve_button.clicked.connect(self.solve_equation)
        self.plot_button.clicked.connect(self.plot_function)
        self.command_input.returnPressed.connect(self.run_command)
        self.command_button.clicked.connect(self.run_command)
        self.copy_button.clicked.connect(self.copy_last_output)  # Connect copy button
        # Connect checkbox toggled signals
        for checkbox in self.plot_checkboxes:
            checkbox.toggled.connect(self._handle_plot_checkbox_toggle)

    def _create_menus(self):
        menu_bar = self.menuBar()
        plot_menu = menu_bar.addMenu("&Plot")

        save_pdf_action = QAction("Save as PDF", self)
        save_pdf_action.setShortcut(QKeySequence.Save)
        save_pdf_action.triggered.connect(self.save_plot_pdf)
        plot_menu.addAction(save_pdf_action)

    def _show_error(self, message):
        self.result_output.append(f"<font color='red'>Error: {message}</font>")

    def _show_result(self, message):
        self.result_output.append(str(message))

    def _get_sympy_expr(self, input_widget=None):
        if input_widget is None:
            self._show_error("Internal error: Input field not specified for parsing.")
            return None

        expr_str = input_widget.text()
        if not expr_str:
            self._show_error(f"{input_widget.objectName() or 'Input'} field is empty.")
            return None
        try:
            x = symbols('x')
            expr = parse_expr(expr_str)
            return expr, x
        except (SympifyError, SyntaxError, TypeError, AttributeError) as e:
            self._show_error(f"Invalid expression in '{input_widget.objectName()}': {e}")
            return None
        except Exception as e:
            self._show_error(f"Error parsing expression in '{input_widget.objectName()}': {e}")
            return None

    def evaluate_expression(self):
        expr_str = self.general_expression_input.text()
        result = self._get_sympy_expr(self.general_expression_input)
        if result:
            self.general_expression_input.add_to_history(expr_str)
            expr, x = result
            try:
                if not expr.free_symbols:
                    value = expr.evalf()
                    self._show_result(f"Expression: {expr}\nEvaluated Value: {value}")
                else:
                    self._show_result(f"Parsed Expression: {expr}")
            except Exception as e:
                self._show_error(f"Could not evaluate: {e}")
            self.general_expression_input.clear()

    def calculate_derivative(self):
        result = self._get_sympy_expr(self.function_input)
        if result:
            expr, x = result
            self.function_input.add_to_history(self.function_input.text())
            try:
                derivative = diff(expr, x)
                self._show_result(f"Function: f(x) = {expr}\nDerivative: f'(x) = {derivative}")
            except Exception as e:
                self._show_error(f"Could not compute derivative: {e}")

    def calculate_integral(self):
        result = self._get_sympy_expr(self.function_input)
        if result:
            expr, x = result
            self.function_input.add_to_history(self.function_input.text())
            try:
                integral = integrate(expr, x)
                self._show_result(f"Function: f(x) = {expr}\nIntegral: ∫f(x)dx = {integral}")
            except Exception as e:
                self._show_error(f"Could not compute integral: {e}")

    def solve_equation(self):
        result = self._get_sympy_expr(self.function_input)
        if result:
            expr, x = result
            self.function_input.add_to_history(self.function_input.text())
            try:
                solutions = solve(expr, x)
                if solutions:
                    self._show_result(f"Equation: {expr} = 0\nSolutions for x: {solutions}")
                else:
                    self._show_result(f"Equation: {expr} = 0\nNo simple symbolic solutions found.")
            except NotImplementedError:
                self._show_error(f"Solving for {expr} = 0 is not implemented or too complex.")
            except Exception as e:
                self._show_error(f"Could not solve equation: {e}")

    def plot_function(self):
        expr_str = self.function_input.text()
        result = self._get_sympy_expr(self.function_input)
        if not result:
            return

        self.function_input.add_to_history(expr_str)
        expr, x = result
        self.current_plot_expr = expr
        self.current_plot_x = x

        # --- Parameter Handling ---
        parameters = expr.free_symbols - {x}
        self.current_plot_params = {str(p): p for p in parameters}

        # Store previous parameter states before clearing
        previous_param_state = {}
        for name, slider in self.parameter_sliders.items():
            if name in self.parameter_min_inputs and name in self.parameter_max_inputs:
                previous_param_state[name] = {
                    'value': slider.value(),
                    'min_text': self.parameter_min_inputs[name].text(),
                    'max_text': self.parameter_max_inputs[name].text()
                }

        # Clear previous sliders and labels more robustly
        while self.parameter_layout.count() > 0:
            label_item = self.parameter_layout.takeAt(0)
            field_item = self.parameter_layout.takeAt(0)

            if label_item:
                widget = label_item.widget()
                if widget:
                    widget.deleteLater()

            if field_item:
                widget = field_item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    layout = field_item.layout()
                    if layout:
                        while layout.count() > 0:
                            child_item = layout.takeAt(0)
                            if child_item:
                                child_widget = child_item.widget()
                                if child_widget:
                                    child_widget.deleteLater()
                        layout.deleteLater()

        self.parameter_sliders.clear()
        self.parameter_labels.clear()
        self.parameter_min_inputs.clear()
        self.parameter_max_inputs.clear()

        if parameters:
            self.parameter_group.setVisible(True)
            for param in parameters:
                param_name = str(param)

                # --- Create Widgets ---
                slider = QSlider(Qt.Horizontal)
                label = QLabel() # Label text set later
                min_input = QLineEdit()
                min_input.setFixedWidth(50)
                max_input = QLineEdit()
                max_input.setFixedWidth(50)

                # Set object names for later lookup/debugging if needed
                slider.setObjectName(param_name)
                min_input.setObjectName(f"min_{param_name}")
                max_input.setObjectName(f"max_{param_name}")

                # --- Store Widgets (before potential state restoration) ---
                self.parameter_sliders[param_name] = slider
                self.parameter_labels[param_name] = label
                self.parameter_min_inputs[param_name] = min_input
                self.parameter_max_inputs[param_name] = max_input

                # --- Restore State or Set Defaults ---
                if param_name in previous_param_state:
                    # Restore previous state
                    state = previous_param_state[param_name]
                    min_input.setText(state['min_text'])
                    max_input.setText(state['max_text'])
                    # Update range first based on restored text
                    self._update_slider_range(param_name) # This sets range and might clamp value
                    # Explicitly set the stored value *after* range is set
                    slider.setValue(state['value'])
                    # Update label based on the final restored value
                    self._update_parameter_label(param_name, state['value'])
                else:
                    # Set default state for new parameters
                    min_input.setText("-10.0")
                    max_input.setText("10.0")
                    slider.setRange(-100, 100)
                    slider.setValue(10) # Default value 1.0
                    label.setText("1.0") # Default label

                # --- Connect Signals ---
                slider.valueChanged.connect(lambda value, p=param_name: self._update_parameter_label(p, value))
                slider.valueChanged.connect(self._update_plot_with_parameters)
                min_input.editingFinished.connect(lambda p=param_name: self._update_slider_range(p))
                max_input.editingFinished.connect(lambda p=param_name: self._update_slider_range(p))

                # --- Layout ---
                h_layout = QHBoxLayout()
                h_layout.addWidget(label) # Value label first
                h_layout.addWidget(QLabel("Min:"))
                h_layout.addWidget(min_input)
                h_layout.addWidget(slider)
                h_layout.addWidget(QLabel("Max:"))
                h_layout.addWidget(max_input)
                self.parameter_layout.addRow(f"{param_name} = ", h_layout)

        else:
            self.parameter_group.setVisible(False)
        # --- End Parameter Handling ---

        # Trigger the actual plot update
        self._update_plot_with_parameters()

    def _update_slider_range(self, param_name):
        """Updates the range of a parameter slider based on min/max inputs."""
        if param_name not in self.parameter_sliders:
            return

        min_input = self.parameter_min_inputs[param_name]
        max_input = self.parameter_max_inputs[param_name]
        slider = self.parameter_sliders[param_name]

        try:
            min_val = float(min_input.text())
            max_val = float(max_input.text())

            if min_val >= max_val:
                self._show_error(f"Parameter '{param_name}': Min range must be less than Max range.")
                # Restore previous valid text if possible
                try:
                    prev_min = slider.minimum() / 10.0
                    prev_max = slider.maximum() / 10.0
                    min_input.setText(str(prev_min))
                    max_input.setText(str(prev_max))
                except Exception: # Fallback if range wasn't set yet
                    min_input.setText("-10.0")
                    max_input.setText("10.0")
                return

            current_value_float = slider.value() / 10.0
            # Set range before potentially clipping value
            slider.setRange(int(min_val * 10), int(max_val * 10))

            # Ensure the current value is within the new range
            new_slider_value = int(np.clip(current_value_float, min_val, max_val) * 10)
            # Use blockSignals to prevent valueChanged emission if setValue changes the value
            slider.blockSignals(True)
            slider.setValue(new_slider_value)
            slider.blockSignals(False)

            # Update the label immediately
            self._update_parameter_label(param_name, new_slider_value)

        except ValueError:
            self._show_error(f"Parameter '{param_name}': Invalid number format in Min/Max range.")
            # Restore previous valid text if possible
            try:
                prev_min = slider.minimum() / 10.0
                prev_max = slider.maximum() / 10.0
                min_input.setText(str(prev_min))
                max_input.setText(str(prev_max))
            except Exception: # Fallback
                min_input.setText("-10.0")
                max_input.setText("10.0")

    def _update_parameter_label(self, param_name, value):
        """Updates the label next to a parameter slider."""
        if param_name in self.parameter_labels:
            float_value = value / 10.0
            self.parameter_labels[param_name].setText(f"{float_value:.2f}")

    def _handle_plot_checkbox_toggle(self, checked):
        """Handles plot checkbox state changes, ensures at least one is checked, and replots."""
        sender = self.sender()
        if not sender:
            return

        # Count how many checkboxes are checked
        checked_count = sum(1 for cb in self.plot_checkboxes if cb.isChecked())

        # If the user just unchecked the last checked box, re-check it
        if checked_count == 0 and not checked: # 'checked' is False if the signal was emitted due to unchecking
             sender.setChecked(True)
             return # Prevent replotting since the state didn't effectively change

        # Replot only if a function has been plotted before
        if self.current_plot_expr:
            self._update_plot_with_parameters()

    def _update_plot_with_parameters(self):
        """Handles the actual plotting based on current expression and parameter values."""
        if not self.current_plot_expr or not self.current_plot_x:
            return

        expr = self.current_plot_expr
        x = self.current_plot_x

        param_values = {}
        for name, slider in self.parameter_sliders.items():
            param_values[self.current_plot_params[name]] = slider.value() / 10.0

        if param_values:
            try:
                expr_substituted = expr.subs(param_values)
            except Exception as e:
                self._show_error(f"Error substituting parameters: {e}")
                return
        else:
            expr_substituted = expr

        if x not in expr_substituted.free_symbols and expr_substituted.free_symbols:
            self._show_error(f"Expression must contain '{x}' after parameter substitution to be plotted.")
            if self._canvas:
                try:
                    self._canvas.figure.clf()
                    ax = self._canvas.figure.subplots()
                    ax.set_title("Invalid Expression for Plotting")
                    self._canvas.draw()
                except Exception as ce:
                    print(f"Error clearing canvas: {ce}")
            return

        try:
            x_min = float(self.plot_x_min_input.text())
            x_max = float(self.plot_x_max_input.text())
            num_points_str = self.plot_num_points_input.text()
            user_title = self.plot_title_input.text()
            x_label = self.plot_x_label_input.text()
            y_label_user = self.plot_y_label_input.text()
            y_min_str = self.plot_y_min_input.text()
            y_max_str = self.plot_y_max_input.text()

            try:
                num_points = int(num_points_str)
                if num_points <= 1:
                    raise ValueError("Number of points must be greater than 1.")
            except ValueError as e:
                self._show_error(f"Invalid number of points: {e}")
                return

            plot_real = self.plot_real_check.isChecked()
            plot_imag = self.plot_imag_check.isChecked()
            plot_abs = self.plot_abs_check.isChecked()
            plot_arg = self.plot_arg_check.isChecked()

            if x_min >= x_max:
                self._show_error("X Min must be less than X Max.")
                return

            y_lim = None
            try:
                if y_min_str and y_max_str:
                    y_min = float(y_min_str)
                    y_max = float(y_max_str)
                    if y_min < y_max:
                        y_lim = (y_min, y_max)
                    else:
                        self._show_error("Y Min must be less than Y Max.")
                elif y_min_str or y_max_str:
                    self._show_result("Warning: Both Y Min and Y Max must be provided for Y limits.")
            except ValueError:
                self._show_error("Invalid input for Y limits (must be numbers).")

            if not self._canvas:
                self._canvas = FigureCanvas(Figure(figsize=(5, 4)))
                self.plot_layout.addWidget(self._canvas)
            else:
                self._canvas.figure.clf()

            ax = self._canvas.figure.subplots()

            try:
                f_lambdified = lambdify(x, expr_substituted, modules=['scipy', 'numpy'])
            except Exception as e:
                self._show_error(f"Could not lambdify function: {e}")
                ax.clear()
                self._canvas.draw()
                return

            x_vals = np.linspace(x_min, x_max, num_points)

            try:
                y_vals = f_lambdified(x_vals)
                if not isinstance(y_vals, np.ndarray):
                    y_vals = np.full_like(x_vals, fill_value=y_vals, dtype=np.result_type(y_vals))
            except Exception as e:
                ax.clear()
                ax.text(0.5, 0.5, f"Error evaluating function:\n{e}",
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, color='red')
                self._show_error(f"Error evaluating function for plotting: {e}")
                self._canvas.draw()
                return

            plotted_something = False
            current_expr_latex = latex(expr)

            """# Determine which components to plot based on checkboxes
            plot_real = self.plot_real_check.isChecked()
            plot_imag = self.plot_imag_check.isChecked()
            plot_abs = self.plot_abs_check.isChecked()
            plot_arg = self.plot_arg_check.isChecked()"""

            lines_plotted = 0

            # Plot explicitly checked components
            if plot_real:
                ax.plot(x_vals, np.real(y_vals), label='Re(f)')
                plotted_something = True
                lines_plotted += 1
            if plot_imag:
                ax.plot(x_vals, np.imag(y_vals), label='Im(f)')
                plotted_something = True
                lines_plotted += 1
            if plot_abs:
                ax.plot(x_vals, np.abs(y_vals), label='Abs(f)')
                plotted_something = True
                lines_plotted += 1
            if plot_arg:
                ax.plot(x_vals, np.angle(y_vals), label='Arg(f)')
                plotted_something = True
                lines_plotted += 1

            if not plotted_something:
                self._show_error("Nothing selected to plot.") # Should not happen
                ax.clear()
                self._canvas.draw()
                return

            ax.set_title(user_title if user_title else f"$f(x) = {current_expr_latex}$")
            ax.set_xlabel(x_label if x_label else 'x')
            ax.set_ylabel(y_label_user if y_label_user else 'f(x)')

            if y_lim:
                ax.set_ylim(y_lim)

            # Show legend only if more than one line was plotted
            if lines_plotted > 1:
                ax.legend()
            else:
                # Remove legend if it exists and only one line is plotted
                if ax.get_legend():
                    ax.get_legend().remove()

            ax.grid(True)
            self._canvas.draw()

        except ValueError as e:
            self._show_error(f"Invalid input for plot parameters: {e}")
            if self._canvas:
                try:
                    self._canvas.figure.clf()
                    ax = self._canvas.figure.subplots()
                    ax.set_title("Plotting Error")
                    ax.text(0.5, 0.5, f"Invalid input:\n{e}",
                            horizontalalignment='center', verticalalignment='center',
                            transform=ax.transAxes, color='red')
                    self._canvas.draw()
                except Exception as ce:
                    print(f"Error clearing canvas after ValueError: {ce}")
        except Exception as e:
            self._show_error(f"Plotting failed: {e}")
            if self._canvas:
                try:
                    self._canvas.figure.clf()
                    ax = self._canvas.figure.subplots()
                    ax.set_title("Plotting Error")
                    ax.text(0.5, 0.5, f"An error occurred:\n{e}",
                            horizontalalignment='center', verticalalignment='center',
                            transform=ax.transAxes, color='red')
                    self._canvas.draw()
                except Exception as ce:
                    print(f"Error clearing canvas after general Exception: {ce}")

    def run_command(self):
        command_str = self.command_input.text()
        if not command_str:
            self._show_error("Command field is empty.")
            return

        try:
            result = parse_expr(command_str)

            if hasattr(result, 'doit'):
                result = result.doit()

            self.command_input.add_to_history(command_str)
            self._show_result(f"Command: {command_str}\nResult: {result}")
            self.command_input.clear()
            self.general_expression_input.clear()
            self.function_input.clear()
        except (SympifyError, SyntaxError, TypeError, NameError, AttributeError, ValueError) as e:
            self._show_error(f"Invalid command, syntax, or symbol usage: {e}")
        except Exception as e:
            self._show_error(f"Command execution failed: {e}")

    def copy_last_output(self):
        full_text = self.result_output.toPlainText()
        if not full_text:
            self._show_result("Nothing to copy.")
            return

        lines = full_text.strip().split('\n')
        if not lines:
            self._show_result("Nothing to copy.")
            return

        last_result_line = ""
        prefixes_to_skip = ["Expression:", "Function:", "Equation:", "Command:", "Plotted function:"]
        prefixes_for_result = ["Result:", "Evaluated Value:", "Derivative: f'(x) = ", "Integral: ∫f(x)dx = ", "Solutions for x:"]

        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if not line:
                continue

            found_prefix = False
            for prefix in prefixes_for_result:
                if line.startswith(prefix):
                    last_result_line = line[len(prefix):].strip()
                    found_prefix = True
                    break
            if found_prefix:
                break

            skip_line = False
            for prefix in prefixes_to_skip:
                if line.startswith(prefix):
                    skip_line = True
                    break
            if skip_line:
                continue

            if not found_prefix and not skip_line:
                last_result_line = line
                break

        if last_result_line:
            clipboard = QApplication.clipboard()
            clipboard.setText(last_result_line)
            self._show_result(f"Copied: {last_result_line}")
        else:
            self._show_result("Could not extract last result to copy.")

    def save_plot_pdf(self):
        if not self._canvas:
            self._show_error("Nothing to save. Please plot a function first.")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Plot as PDF",
            "",
            "PDF Files (*.pdf);;All Files (*)",
            options=options
        )

        if file_path:
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'

            fig = self._canvas.figure
            param_text_object = None # To store the text object for removal

            try:
                # Add parameter text if parameters exist
                if self.parameter_sliders:
                    param_strings = []
                    for name, slider in self.parameter_sliders.items():
                        value = slider.value() / 10.0
                        param_strings.append(f"{name}={value:.2f}")
                    param_text = ", ".join(param_strings)
                    # Add text at the bottom center of the figure
                    param_text_object = fig.text(0.5, 0.01, param_text, ha='center', va='bottom', fontsize=12)

                # Adjust layout to prevent overlap (optional, might affect appearance)
                # fig.tight_layout(rect=[0, 0.03, 1, 1]) # Adjust rect to leave space for text

                fig.savefig(file_path, format='pdf', bbox_inches='tight') # Use bbox_inches='tight' for better layout
                self._show_result(f"Plot saved to {file_path}")

            except Exception as e:
                self._show_error(f"Failed to save plot as PDF: {e}")
            finally:
                # Remove the added text object after saving
                if param_text_object:
                    param_text_object.remove()
                # Redraw canvas to reflect the removal (if it was visible)
                # self._canvas.draw_idle() # Or self._canvas.draw() if immediate update needed
        else:
            self._show_result("Save operation cancelled.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
