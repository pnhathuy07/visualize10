import numpy as np
import math
from sympy import sympify, latex
from decimal import Decimal
import re
import os

from bokeh.layouts import column, row
from bokeh.models import HoverTool, CrosshairTool, CustomJS, Slider
from bokeh.plotting import ColumnDataSource, figure, output_file, show

import algorithms as alg
from algorithms import sub, inp

#################################################
# Logistic: A / (1 + e ** (-1 * B * (X - C)))
# Logarithm: log(X) * A + B
# Pythagoras: sqrt(A**2 - X**2)
# Tangent: tan(X) * A
# Sine: sin(X * A + B) * C + D
#################################################

# --Function setup-- #
equ = inp('Please type in your function.', 'f(X)').replace('^', '**')

latex = alg.LatexLabel(
    text=latex(sympify(equ.lower())),
    x=80,
    y=810,
    x_units="screen",
    y_units="screen",
    render_mode="css",
    text_font_size="48px",
    background_fill_alpha=0,
)

# --Graph setup-- #
try:
    range = sorted(map(lambda x: float(x), [inp('Where do you want your graph to start at?', f'X{sub[1]}'), inp('Where do you want your graph to end at?', f'X{sub[2]}')]))
    size = math.ceil(range[1] - range[0])
    assert size > 0
    detail = 500 + size * 500
except: raise ValueError('Invalid input: Range must be a real number and must be greater than 0.')

x = np.linspace(range[0], range[1], detail)
y = ["None"] * len(x)

# --Tools setup-- #
hoverTool = HoverTool(
    mode='vline',
    tooltips="""
        <div>
            <div>
                <span style="font-size: 12px; font-weight: bold; color: #F78C6C">y</span>
                <span style="font-size: 32px; font-weight: bold;">@y{1.1111}</span>
                <span style="font-size: 12px; font-weight: bold; color: #F78C6C">x</span>
                <span style="font-size: 24px; font-weight: bold; color: #966;">@x{1.11}</span>
            </div>
        </div>
    """
)

crosshairTool = CrosshairTool(dimensions='height', line_color='#1F77B4', line_width=4, line_alpha=.5)

source = ColumnDataSource(data=dict(x=x, y=y))
plot = figure(plot_width=1600, plot_height=900, tools='pan,wheel_zoom,box_zoom,undo,redo,reset,save', active_scroll="wheel_zoom", toolbar_location="below")
plot.add_layout(latex)
plot.line('x', 'y', source=source, line_width=4, line_alpha=1)

plot.add_tools(hoverTool, crosshairTool)
plot.toolbar.active_inspect = [hoverTool]
plot.toolbar.autohide = True

# --Variable setup
var = list(dict.fromkeys([c for c in equ if (c.isupper() and c not in ['E', 'X'])]))
if not len(var) > 0: raise ValueError('Invalid input: Function must have at least one adjustable variable.')
print('\nHere are the variables', var)

sliders = {}
for i in var:
    size = abs(float(inp(f'What do you want the size of the slider for {i} to be?', f'{i}size')))
    assert not size == 0

    value = 1
    if size < 1: value = size

    shift = 2
    stepdefault = str(10 ** (int(re.sub(r'^(.+?)[+]', '+', re.sub(r'^(.+?)[-]', '-', str('%.1E' % Decimal(size))))) - shift))

    step = abs(float(inp(f'How much do you want the slider for {i} to scroll each time?', f'{i}step', stepdefault)))
    assert not (step == 0 or step > size)

    sliders[i] = Slider(start=-1 * size, end=size, value=value, step=step, title=i.lower())

# --Code setup-- #
constString = ""
for i in var:
    constString += "const " + i + " = sliders['" + i + "'] .value;"

code = """
    const data = source.data;
    """ + constString + """
    const X = data['x'];
    const Y = data['y'];
    for (var i = 0; i < X.length; i++) {
        Y[i] = """ + alg.finalizeFunction(equ) + """
    }
    source.change.emit();
"""

print('\nFinal Function:\nf(X) = ' + alg.finalizeFunction(equ).replace('[i]', ''))

callback = CustomJS(args=dict(source=source, sliders=sliders), code=code)

for i in var:
    sliders[i].js_on_change('value', callback)

layout = row(
    plot,
    column(list(sliders.values())),
)

filename = "visual.html"
output_file(filename, title="Visualize 10")
show(layout)

os.startfile(f'{os.path.dirname(os.path.abspath(__file__))}')