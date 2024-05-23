import streamlit as st
from Graph import TextGraph  # 假设你的TextGraph类在textgraph.py文件中
from datetime import datetime

# 创建TextGraph实例
text_graph = TextGraph('text.txt')

st.set_option('deprecation.showPyplotGlobalUse', False)
if 'cur_idx' not in st.session_state:
    st.session_state.cur_idx = 10086
    st.session_state.Rpath, st.session_state.RPlot_list = text_graph.randomWalk()
    st.session_state.save = datetime.now().strftime("%Y-%m-%d %H.%M.%S")

# Streamlit应用的标题
st.title('Text Analysis and Random Walk')
# 添加侧边栏选项
with st.sidebar:
    choice = st.radio(
        "Choose an action",
        ('Show Graph', 'Generate New Text', 'Query Bridge Words', 'Show Shortest Path', 'Random Walk')
    )

# 根据用户的选择执行不同的操作
if choice == 'Show Graph':
    st.header('Text Graph Visualization')
    p = text_graph.showDirectedGraph('', with_edge_label=True)
    p.savefig('Graph.png')
    st.pyplot(p)

elif choice == 'Generate New Text':
    st.header('Generate New Text')
    input_text = st.text_input('Please input sentence:')
    if st.button('Generate New Text:'):
        Plot_list,answer = text_graph.generateNewText(input_text)
        st.markdown(answer,unsafe_allow_html=True)
        if Plot_list is not None:
            for plot in Plot_list:
                st.pyplot(plot)
elif choice == 'Query Bridge Words':
    st.header('Query Bridge Words')
    word1 = st.text_input('Please input word_1:')
    word2 = st.text_input('Please input word_2:')

    if st.button('Calculate the Bridge Words'):
        Plot_list, answer = text_graph.queryBridgeWords(word1, word2)
        st.markdown(answer,unsafe_allow_html=True)
        if Plot_list is not None:
            for plot in Plot_list:
                st.pyplot(plot)
elif choice == 'Show Shortest Path':
    st.header('Show Shortest Path')
    word1 = st.text_input('Please input word_1:')
    word2 = st.text_input('Please input word_2:')

    if word1 != '' and word2 != '':
        st.write(f'Below are all the shortest paths from {word1} to {word2}.')
    elif word2 == '':
        word2 = None
        st.write(f'Below are all the shortest paths from {word1} to All nodes.')
    if st.button('Calculate the Shortest Paths'):
        Plot_list = text_graph.highlight_shortest_path(word1, word2)
        if Plot_list is not None:
            for plot in Plot_list:
                st.pyplot(plot)
        else:
            st.write(f'There is no path between {word1} and {word2}')
elif choice == 'Random Walk':
    if st.session_state.cur_idx <= len(st.session_state.Rpath) - 1:
        st.write('You can click the Random button to take the next step in the random walk:')
    else:
        st.write('This Random Walk is over!')
        st.write('You can click the button to proceed to a new Random Walk')

    if st.button('Random Walk restart:'):
        st.session_state.cur_idx = 0
        st.session_state.Rpath, st.session_state.RPlot_list = text_graph.randomWalk()
        st.session_state.save = datetime.now().strftime("%Y-%m-%d %H.%M.%S")
        st.write(f'The System has selected a random start_node {st.session_state.Rpath[st.session_state.cur_idx]}')
        st.pyplot(st.session_state.RPlot_list[0])
        with open('Random_walk/Random_walk_output_' + st.session_state.save + '.txt', 'w') as f:
            f.write(''.join(st.session_state.Rpath[0:1]))

    if st.button('Random Walk Next:') and st.session_state.cur_idx <= len(st.session_state.RPlot_list) - 1:
        st.pyplot(st.session_state.RPlot_list[st.session_state.cur_idx])
        st.session_state.cur_idx += 1
        with open('Random_walk/Random_walk_output_' + st.session_state.save + '.txt', 'w') as f:
            st.write(' '.join(st.session_state.Rpath[0:st.session_state.cur_idx]))
            f.write(' '.join(st.session_state.Rpath[0:st.session_state.cur_idx]))
