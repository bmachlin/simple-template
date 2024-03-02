# Simple Template

## Overview

Simple Template is a simple templating library for developing websites. You define HTML-esque templates, reference them in your HTML files, then run the build process.

Template files have a .tml ([Template Markup Language](Template.md)) extension and live together in one folder. The have the form:
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
Which will build as:
```
<div class="thing-container">
    <p>default</p>
</div>
<div class="thing-container">
    <p>param value</p>
</div>
```
The first section is just the id/tag name. It's how you'll reference the template in your HTML files.

The second (optional) section defines default values for the template's variables.

The third section is the actual template, including variables.

Templates can reference other templates (but be wary of dependency cycles).

See [Template.md](Template.md) for full details.

## Workflow

### Build
To build your website, run:

`python build.py [config_path]`

or to achieve live-reload, use:

`python build.py [config_path] watch`

along with a live-reload server.

## Config Options

Various options can be set in a config file or with a dictionary if accessing the library using python.

You can specify a config file path as a command line argument with build.py or watch.py.

### Config Options Explained
| Key | Value | Default |Explanation |
|------|-------|---------|------------|
|TEMPLATE_VAR_START|string*|\{\{|The beginning sentinel for a variable within a template.|
|TEMPLATE_VAR_END|string*|\}\}|The ending sentinel for a variable within a template.|
|TEMPLATE_SECTION_SPLIT|string*|\n%\n|The sequence used to separate the sections of a template.|
|INNER_HTML_VAR|string*|\_inner\_|The template variable that inserts the innerHTML of the template.|
|EMPTY_VAR_REPLACE|boolean|true|If false, variables in a template that are not assigned when the template is used, and have no default with not be replaced. So {{var}} will appear in the HTML literally.|
|EMPTY_VAR_VALUE|string*|""|The string that will replace unassigned variables if EMPTY_VAR_REPLACE is true. So {{var}} will be replaced by the empty string by default.|
|INPUT_DIR|string|.|Path to the directory to scan for HTML files.
|OUTPUT_DIR|string|./output|Path to a directory to output the contents of INPUT_DIR.|
|TEMPLATE_DIR|string|.|Path to a directory to scan for ```.tml``` template files.|
|EXCLUDE_ALL|array of strings|["\*/.git/\*, ...]|File patterns to ignore in all parts of the process.|
|EXCLUDE_HTML|array of strings|[ ]|File patterns for HTML files ignore|
|EXCLUDE_TEMPLATE|array of strings|[ ]|File patterns for template files ignore|
|EXCLUDE_COPY|array of strings|[ ]|File patterns for files in INPUT_DIR that should not be copied to OUTPUT_DIR|
|OVERWRITE_ALLOWED|boolean|false|Defines if files can be overwritten during the build. E.g. if INPUT_DIR and OUTPUT_DIR are the same.|



\*These strings will interact with HTML and so you should be wary of values that would cause problems (like < or >) or be found in normal HTML files (like "class" or </).

# Drawbacks

- lots of file copying
- two git repos potentially, or you can use a web hook like Github Actions
- HTML files output with funky formatting (from BeautifulSoup)

# TODOs

- Selective processing when detecting a file changed (as opposed to just running the whole thing again)
- Don't lose HTML file formatting when building