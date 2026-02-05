from jinja2 import Environment

import utils as fn


class ExampleForm(fn.Form):
    def validate(self):
        self.error["field"] = "Invalid."


def test_form_validation_runs():
    form = ExampleForm({"field": "value"})
    assert not form.is_valid()
    assert form.error["field"] == "Invalid."


def test_jinja_ext_macro_def():
    ext = fn.JinjaExt(Environment())
    source = "%def\n  Hello"
    result = ext.preprocess(source, "Macros/Sample.html")
    assert result.startswith("%macro Sample()")
    assert "%endmacro" in result


def test_jinja_ext_inline_component():
    ext = fn.JinjaExt(Environment())
    source = "<Alert />"
    result = ext.preprocess(source, "page.html")
    assert "{{ ui.Alert() }}" in result
