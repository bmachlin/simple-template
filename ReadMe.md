# Simple Template

Simple Template is a simple templating library for developing websites. You define HTML-esque templates, reference them in your HTML files, then run the build process.

Template files have a .tml (Template Markup Language) extension and live together in one folder. The have the form:
```
thing
%
var=default
%
<div class="thing-container">
    <p>{{var}}</p>
</div>
```
And can be used like so:
```
...
<thing></thing>
<thing var="param value"></thing>
...
```
Which will build to:
```
<div class="thing-container">
    <p>default</p>
</div>
<div class="thing-container">
    <p>param value</p>
</div>
```
The first section is just the id/tag name. It's how you'll reference the template in your HTML files.

The second (optional) section defines (optional) default values for the template's variables.

The third section is the actual template, including variables.

Templates can reference other templates (but be wary of dependency cycles).

## Workflow

### Build
To build your website, run:

```python run.py [options]```

...

# Drawbacks

- lots of copying
- two git repos potentially
- easy to accidentally overwrite things

# TODOs

- file and folder exclusion (especially things like \_\_pycache__ and node_modules and .git)
- 