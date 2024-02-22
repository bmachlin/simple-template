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

```python build.py [config_path]```

or to achieve live-reload, use:

```python watch.py [path_to_watch_folder] [config_path]```
...

## Config Options

Various options can be set in a config file or with a dictionary if accessing the library using python.

You can specify a config file path as a command line argument with build.py or watch.py.

### Config Options Explained
| Name | Value | Default |Explanation |
|------|-------|---------|------------|
|TEMPLATE_VAR_START|string*|\{\{|The beginning sentinel for a variable within a template.|
|TEMPLATE_VAR_END|string*|\}\}|The ending sentinel for a variable within a template.|
|TEMPLATE_SECTION_SPLIT|string*|\n%\n|The sequence used to separate the sections of a template.|
|EMPTY_VAR_REPLACE|boolean|true|If false, variables in a template that are not assigned when the template is used, and have no default with not be replaced. So {{var}} will appear in the HTML literally.|
|EMPTY_VAR_VALUE|string*|""|The string that will replace unassigned variables if EMPTY_VAR_REPLACE is true. So {{var}} will be replaced by the empty string by default.|
|INPUT_DIR|string|.|Path to the directory to scan for HTML files.
|OUTPUT_DIR|string|./output|Path to a directory to output the contents of INPUT_DIR. Does not have to exist beforehand.|
|OUTPUT_DIR|string|templates|Path to a directory of ```.tml``` template files.|
|EXCLUDE_ALL|array of strings|["\*/.git/\*, ...]|File patterns to ignore in all parts of the process.|
|EXCLUDE_HTML|array of strings|[ ]|File patterns for HTML files ignore|
|EXCLUDE_TEMPLATE|array of strings|[ ]|File patterns for template files ignore|
|EXCLUDE_COPY|array of strings|[ ]|File patterns for files in INPUT_DIR that should not be copied to OUTPUT_DIR|


\*These strings will interact with HTML and so you should be wary of values that would cause problems (like < or >) or be found in normal HTML files (like "class" or </).

# Drawbacks

- lots of copying
- two git repos potentially
- easy to accidentally overwrite things

# TODOs

- Selective processing when detecting a file changed (as opposed to just running the whole thing again)