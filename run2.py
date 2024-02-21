from SimpleTemplate import SimpleTemplate

st = SimpleTemplate(configPath="./tml_config.json")
st.SetInputDir("../bmachlin")
st.SetOutputDir("../output")
st.SetTemplateDir("../bmachlin/templates")

st.LoadHtmlFiles()

st.LoadTemplates()

st.FindTemplateDependencies()

st.FindHtmlDependencies()

st.TopologicalSort()

st.FillAllFiles()

st.CopyInputDirectory()

st.OutputProcessedFiles()