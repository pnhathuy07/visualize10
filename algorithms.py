import re
import sys

from bokeh.models import Label
from bokeh.plotting import figure, show
from bokeh.util.compiler import TypeScript

TS_CODE = """
import * as p from "core/properties"
import {Label, LabelView} from "models/annotations/label"
declare const katex: any

export class LatexLabelView extends LabelView {
  model: LatexLabel

  render(): void {
    //--- Start of copied section from ``Label.render`` implementation

    // Here because AngleSpec does units tranform and label doesn't support specs
    let angle: number
    switch (this.model.angle_units) {
      case "rad": {
        angle = -this.model.angle
        break
      }
      case "deg": {
        angle = (-this.model.angle * Math.PI) / 180.0
        break
      }
      default:
        throw new Error("unreachable code")
    }

    const panel = this.panel != null ? this.panel : this.plot_view.frame

    let sx = this.model.x_units == "data" ? this.coordinates.x_scale.compute(this.model.x) : panel.xview.compute(this.model.x)
    let sy = this.model.y_units == "data" ? this.coordinates.y_scale.compute(this.model.y) : panel.yview.compute(this.model.y)

    sx += this.model.x_offset
    sy -= this.model.y_offset

    //--- End of copied section from ``Label.render`` implementation
    // Must render as superpositioned div (not on canvas) so that KaTex
    // css can properly style the text
    this._css_text(this.layer.ctx, "", sx, sy, angle)

    // ``katex`` is loaded into the global window at runtime
    // katex.renderToString returns a html ``span`` element
    katex.render(this.model.text, this.el, {displayMode: true})
  }
}

export namespace LatexLabel {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Label.Props
}

export interface LatexLabel extends LatexLabel.Attrs {}

export class LatexLabel extends Label {
  properties: LatexLabel.Props
  __view_type__: LatexLabelView

  constructor(attrs?: Partial<LatexLabel.Attrs>) {
    super(attrs)
  }

  static init_LatexLabel() {
    this.prototype.default_view = LatexLabelView
  }
}
"""

class LatexLabel(Label):
    """A subclass of the Bokeh built-in `Label` that supports rendering
    LaTex using the KaTex typesetting library.

    Only the render method of LabelView is overloaded to perform the
    text -> latex (via katex) conversion. Note: ``render_mode="canvas``
    isn't supported and certain DOM manipulation happens in the Label
    superclass implementation that requires explicitly setting
    `render_mode='css'`).
    """
    __javascript__ = ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.js"]
    __css__ = ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.css"]
    __implementation__ = TypeScript(TS_CODE)

def validateSyntax(func):
    """
    Check if the function is valid.

    Arguments: function

    Warning: This function only checks if the function stays in the syntax limit. Further validation will be conducted later when an error is thrown.
    """
    validSyntax = 'abcdefghijklmnopqrstuvwxz1234567890()+-*/^%!'
    for a in func.lower():
        if a not in validSyntax:
            return False
    
    return True

def finalizeFunction(func):
    """
    Returns the final, completed function.

    Arguments: function
    """
    def function(m):
        return m.group(1) + m.group(2).upper()
    func = re.sub(r'([a-z]+\(.*?)', r'Math.\1', func)
    func = re.sub(r'(?<!\.)(?<![a-zA-Z])([a-z]+)(?!\(.*?\))(?!\.)', lambda x: f'Math.{x[1].upper()}', func).replace('X', 'X[i]')
    return func

def inp(message, assign='', default=''):
  __ass = ''
  __def = ''

  if not assign == '': __ass = f'{assign} = '
  if not default == '': __def = f'{bcol.OKCYAN}[Default: {default}]{bcol.ENDC} '

  result = ''

  failedAttempt = 0
  maxfailedAttempt = 10

  while result == '':
    result = input(f'\n{message}\n>>> {__ass}{__def}').strip()

    if result == '':
      if default != '': result = default.strip()
      else: 
        failedAttempt += 1
        print(f'{bcol.FAIL}You cannot leave this field blank. {bcol.BOLD}({str(failedAttempt)} out of {str(maxfailedAttempt)} failed attempt){bcol.ENDC}')

        if failedAttempt >= maxfailedAttempt: 
          print(f'{bcol.WARNING}Session has ended. Exiting application...{bcol.ENDC}')
          sys.exit()


  return result

sub = ['₀', '₁', '₂', '₃', '₄', '₅', '₆', '₇', '₈', '₉']

class bcol:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
