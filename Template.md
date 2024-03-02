# TML- Template Markup Language

#### See [examples](examples/)

## Syntax

# Template Markdown Language - TML
A TML template is a simple format for creating reusable HTML templates.

They consist of 2 or 3 parts: the template name, default values (optional) and HTML. And example might look like this:

    easy-link
    %
    <a href={{link}} target="_blank" rel="noopener">{{_inner_}}</a>

or like this:

    navbar
    %
    text = Back
    %
    <nav>
        <a href=".." class="home">{{text}}</a>
    </nav>

`\n%\n` is the default separator between parts.

In an HTML file your can reference them like this:

    ...
    <navbar></navbar>
    <easy-link link="/index.html"><span style="font-weight: bold;">Go</span> to landing page.</easy-link>
    ...


## HTML

The HTML portion of a TML describes what should be inserted in place of the template. It can include variables wrapped in double braces like so `{{var}}`. There is one special variable, `_inner_` which will be replaced with the innerHTML of the template instance. E.g. In `<thing>Here</thing>`, `_inner_` = `Here`.

## Default Values
Default values can be specified with a simple `x = y`, one per line.
Be careful of quotes, for example, 

    link = /index.html
    text = "Test"
    %
    <a href={{link}}>{{text}}</a>

will be inserted as `<a href=/index.html>"Test"</a>`

The correct format would be 

    link=/index.html
    text=Test
    %
    <a href="{{link}}">{{text}}</a>

or

    link = "/index.html"
    text = Test
    %
    <a href={{link}}>{{text}}</a>

which will both be inserted correctly as `<a href="/index.html">Test</a>`.

## Config Options

| Key | Value | Default |Explanation |
|------|-------|---------|------------|
|TEMPLATE_VAR_START|string*|\{\{|The beginning sentinel for a variable within a template.|
|TEMPLATE_VAR_END|string*|\}\}|The ending sentinel for a variable within a template.|
|TEMPLATE_SECTION_SPLIT|string*|\n%\n|The sequence used to separate the sections of a template.|
|INNER_HTML_VAR|string*|\_inner\_|The template variable that inserts the innerHTML of the template.|
|EMPTY_VAR_REPLACE|boolean|true|If false, variables in a template that are not assigned when the template is used, and have no default with not be replaced. So {{var}} will appear in the HTML literally.|
|EMPTY_VAR_VALUE|string*|""|The string that will replace unassigned variables if EMPTY_VAR_REPLACE is true. So {{var}} will be replaced by the empty string by default.|

\*These strings will interact with HTML and so you should be wary of values that would cause problems (like < or >) or be found in normal HTML files (like "class" or </).

## Gotchas

## TODOs