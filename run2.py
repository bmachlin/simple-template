from SimpleTemplate import SimpleTemplate

st = SimpleTemplate(configPath="./tml_config.json")
st.SetInputDir("../bmachlin")
st.SetOutputDir("../output")
st.SetTemplateDir("../bmachlin/templates")

st.LoadHtmlFiles()
# print(st.htmlFiles)

st.LoadTemplates()
# print(st.templateFiles)

st.FindTemplateDependencies()
# for t in st.templates:
#     print(t.path, t.dependencies)

st.FindHtmlDependencies()
# for html in st.htmlFiles:
#     print(html.path, html.dependencies)

st.TopologicalSort()

st.FillAllFiles()

st.CopyInputDirectory()

st.OutputProcessedFiles()