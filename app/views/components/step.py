from fasthtml.common import *
import time

from .file_explorer import FileExplorer
from app.agents.state_schema import RetrievalMethod

def Step(
    feedback_question,
    answer,
    retrieved_chunks,
    project_id,
    next_step: int,
    directory_tree_str: str,
    retrieval_method: str,
    quota: tuple[int, int],
    is_last_step=False,
):
    """A step is a intermeidate process to generate a README file. For example, there could be 3 steps where the first step is to generate the entry point of the repository, second step is to generate get_started section and third step is to generate the installation section."""

    common_style = "margin-bottom:1rem;  border: 1px solid #a0a0a0; border-radius: 5px; padding: 10px;"
    scrollable_style = (
        common_style
        + " height: 300px; max-height: 1000px; overflow-y: auto; resize: vertical"
    )
    textarea_style = (
        common_style
        + " min-height: 300px; max-height: 300px; overflow-y: auto; resize: vertical;"
    )
    
    quota_reset_time = round(
        (quota[1] + int(os.getenv("QUOTA_RESET_MINUTES", 30)) * 60 - time.time()) / 60, 2
    )

            
    return Div(id="step")(
        Div(
            cls="control-panel",
            style="display: flex; justify-content: flex-start; align-items: center; margin-bottom: 1rem; gap: 1rem;",
        )(
            Button(
                "Collapse All",
                id="collapse_all_button",
                onclick="toggleAll()",
                cls="toggle-all-btn",
                style="",
            ),
            Div(
                style="display: flex; align-items: center; flex-wrap: nowrap;",
            )(
                Label(
                    "Retrieval Method:",
                    for_="retrieval_method",
                    style="font-size: 0.75rem; margin-right: 0.5rem; margin-bottom: 0; white-space: nowrap;",
                ),
                Select(
                    id="retrieval_method",
                    name="retrieval_method",
                    cls="form-select",
                    hx_post="/update_retrieval_method",
                    hx_trigger="change",
                    hx_swap="none",
                    style="margin-bottom: 0; font-size: 0.75rem; flex-grow: 1; padding-top: 0.25rem; padding-bottom: 0.25rem; padding-left: 0.75rem;",
                )(
                    *[
                        Option(
                            method.value,
                            value=method.name,
                            selected=(method == RetrievalMethod[retrieval_method]),
                        )
                        for method in RetrievalMethod
                    ]
                ),
            ),
            Div(
                id="quota_display",
                style="flex-wrap: nowrap; display: flex; align-items: center;",
            )(
                P(
                    f"Quota: {quota[0] if quota_reset_time > 0 else int(os.getenv("QUOTA_LIMIT", 10))} / Reset in {quota_reset_time if quota_reset_time > 0 else 0} mins",
                    style="font-size: 0.75rem; margin: 0;",
                ),
            ),
        ),
        H4(f"Step {next_step-1}. {feedback_question}"),
        Form(
            id="step_form",
            hx_post=f"step?step_num={next_step - 1}&project_id={project_id}",
            hx_swap="innerHTML",
            hx_target="main",
            hx_target_429="#quota_msg",
            hx_target_500="#error_msg",
            hx_indicator=".btn-loader",
        )(
            Div(cls="horizontal-layout")(
                Div(cls="left-column")(
                    Div(cls="collapsible-section")(
                        H5("Answer", onclick="toggleSection(this)"),
                        Div(cls="section-content")(
                            Textarea(
                                id="answer",
                                name="answer",
                                cls="dynamic-textarea",
                                style=textarea_style,
                            )(answer),
                        ),
                    ),
                    Div(cls="collapsible-section")(
                        H5("Feedback", onclick="toggleSection(this)"),
                        Div(cls="section-content")(
                            Textarea(
                                id="user_feedback",
                                name="user_feedback",
                                placeholder="Enter your feedback here",
                                cls="dynamic-textarea",
                                style=textarea_style,
                            ),
                        ),
                    ),
                ),
                Div(cls="right-column")(
                    Div(cls="collapsible-section")(
                        Div(style="display: flex; align-items: center;")(
                            H5(
                                "Retrieved Code Snippets", onclick="toggleSection(this)"
                            ),
                            Button(
                                "Collapse All",
                                id="collapse_all_button_code_snippets",
                                onclick="toggleAllCodeSnippets()",
                                cls="toggle-all-btn",
                                type="button",
                                style="margin-bottom: 0.5rem; margin-left: 1rem; cursor: pointer; padding: 0.125rem 0.5rem 0.125rem 0.5rem; font-size: 0.75rem; ",
                            ),
                        ),
                        Div(cls="section-content")(
                            Div(
                                style=scrollable_style,
                            )(
                                P(
                                    style="font-size: 0.75rem; margin-bottom: 0.125rem; margin-top: 0.125rem; padding:0;"
                                )(
                                    "An LLM will check if the code snippets are relevant to the answer. If not, it will be shown as None"
                                ),
                                *(
                                    [P("No code snippets are retrieved")]
                                    if not retrieved_chunks
                                    else [
                                        Div(
                                            P(
                                                f"▼ {path.split('/')[-1]}",
                                                style="font-weight: semi-bold; margin-bottom: 0; cursor: pointer;",
                                                onclick=f"toggleCodeSnippet('snippet-{i}')",
                                            ),
                                            Div(
                                                id=f"snippet-{i}",
                                                style="",
                                            )(
                                                Pre(
                                                    style="background-color: transparent; padding: 0; margin: 0;"
                                                )(
                                                    Code(
                                                        chunk,
                                                        style="display: block; width: 100%; white-space: pre-wrap; word-break: break-all;",
                                                    )
                                                )
                                            ),
                                        )
                                        for i, (path, chunk) in enumerate(
                                            retrieved_chunks.items()
                                        )
                                    ]
                                ),
                            ),
                        ),
                    ),
                    Div(cls="collapsible-section")(
                        Div()(
                            Div(style="display: flex; align-items: center;")(
                                H5("File Explorer", onclick="toggleSection(this)"),
                                Button(
                                    "Collapse All",
                                id="toggle-all-btn-file-explorer",
                                cls="toggle-all-btn",
                                type="button",
                                onclick="toggleAllFileExplorer()",
                                style="margin-bottom: 0.5rem; margin-left: 1rem; cursor: pointer; padding: 0.125rem 0.5rem 0.125rem 0.5rem; font-size: 0.75rem;",
                                ),
                                Button(
                                    "Uncheck All",
                                    id="uncheck-all-btn",
                                    type="button",
                                    onclick="uncheckAllFileExplorer()",
                                    style="margin-bottom: 0.5rem; margin-left: 0.5rem; cursor: pointer; padding: 0.125rem 0.5rem 0.125rem 0.5rem; font-size: 0.75rem; ",
                                ),
                            ),
                            P("Select the files that you want to include in the context of the LLM."),
                        ),
                        Div(cls="section-content")(
                            FileExplorer(directory_tree_str, scrollable_style),
                            Input(
                                type="hidden",
                                id="directory_tree_str",
                                name="directory_tree_str",
                                value=directory_tree_str,
                            ),
                        ),
                    ),
                ),
            ),
            Button(
                "Apply Feedback",
                id="apply_feedback_button",
                type="submit",
                cls="btn-loader",
            ),
        ),
        (
            Button(
                "Next Step",
                type="submit",
                cls="btn-loader",
                id="next_step_button",
                hx_post=f"step?step_num={next_step}&project_id={project_id}",
                hx_swap="innerHTML",
                hx_target="main",
                hx_target_429="#quota_msg",
                hx_target_500="#error_msg",
                hx_replace_url="true",
            )
            if not is_last_step
            else Button(
                "Finish",
                type="submit",
                cls="btn-loader",
                hx_post=f"step/final?project_id={project_id}",
                hx_swap="innerHTML",
                hx_target="main",
                hx_target_429="#quota_msg",
                hx_target_500="#error_msg",
                hx_replace_url="true",
            )
        ),
        Script(
            """
(function() {
    const textareas = document.querySelectorAll('.dynamic-textarea');
    textareas.forEach(textarea => {
        textarea.style.height = 'auto';
        textarea.style.height = `${Math.min(textarea.scrollHeight, 600)}px`;
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = `${Math.min(this.scrollHeight, 600)}px`;
        });
    });
})();

function updateTree(tree, fullPath, value) {
    const pathParts = fullPath.split('/');
    const fileName = pathParts.pop();
    const currentLevel = pathParts.reduce((accumulator, path) => accumulator[path], tree);
    currentLevel[fileName] = value;
}

document.addEventListener('change', function(e) {
    if (e.target.matches('.file-explorer input[type="checkbox"]')) {
        let tree = JSON.parse(document.getElementById('directory_tree_str').value);
        updateTree(tree, e.target.value, e.target.checked);
        document.getElementById('directory_tree_str').value = JSON.stringify(tree);
    }
});

function toggleSection(header) {
    const content = header.nextElementSibling;
    content.style.display = content.style.display === 'none' ? 'block' : 'none';
    header.classList.toggle('collapsed');
    updateCollapseAllButton();
}

function updateCollapseAllButton() {
    const button = document.getElementById('collapse_all_button');
    const sections = document.querySelectorAll('.collapsible-section');
    const allCollapsed = Array.from(sections).every(section => 
        section.querySelector('.section-content').style.display === 'none'
    );
    button.textContent = allCollapsed ? 'Expand All' : 'Collapse All';
}

document.addEventListener('DOMContentLoaded', function() {
    const sections = document.querySelectorAll('.collapsible-section');
    sections.forEach(section => {
        const content = section.querySelector('.section-content');
        content.style.display = 'block';
        section.querySelector('h5').classList.remove('collapsed');
    });
    updateCollapseAllButton();
});

function toggleAll() {
    const button = document.getElementById('collapse_all_button');
    const sections = document.querySelectorAll('.collapsible-section');
    const allCollapsed = Array.from(sections).every(section => 
        section.querySelector('.section-content').style.display === 'none'
    );

    sections.forEach(section => {
        const content = section.querySelector('.section-content');
        const header = section.querySelector('h5');
        content.style.display = allCollapsed ? 'block' : 'none';
        header.classList.toggle('collapsed', !allCollapsed);
    });

    button.textContent = allCollapsed ? 'Collapse All' : 'Expand All';
}

function toggleDirectory(btn, dirName) {
    const dir = document.getElementById('dir-' + dirName);
    if (dir.style.display === 'none') {
        dir.style.display = 'block';
        btn.textContent = `▼ ${dirName}`;
    } else {
        dir.style.display = 'none';
        btn.textContent = `▶ ${dirName}`;
    }
}

function toggleAllFileExplorer() {
    const btn = document.getElementById('toggle-all-btn-file-explorer');
    const allDirs = document.querySelectorAll('.file-explorer ul[id^="dir-"]');
    const allToggleBtns = document.querySelectorAll('.file-explorer-collapse-btn');
    
    if (btn.textContent === 'Collapse All') {
        allDirs.forEach(dir => dir.style.display = 'none');
        allToggleBtns.forEach(toggleBtn => {
            const dirName = toggleBtn.textContent.trim().slice(2);
            toggleBtn.textContent = `▶ ${dirName}`;
        });
        btn.textContent = 'Expand All';
    } else {
        allDirs.forEach(dir => dir.style.display = 'block');
        allToggleBtns.forEach(toggleBtn => {
            const dirName = toggleBtn.textContent.slice(2);
            toggleBtn.textContent = `▼ ${dirName}`;
        });
        btn.textContent = 'Collapse All';
    }
}

function uncheckAllFileExplorer() {
    const checkboxes = document.querySelectorAll('.file-explorer input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.checked = false;
        checkbox.style.backgroundColor = '';
        updateTree(JSON.parse(document.getElementById('directory_tree_str').value), checkbox.value, false);
    });
    const tree = JSON.parse(document.getElementById('directory_tree_str').value);
    document.getElementById('directory_tree_str').value = JSON.stringify(tree);
}

function toggleCodeSnippet(id) {
    const snippet = document.getElementById(id);
    snippet.style.display = snippet.style.display === 'none' ? 'block' : 'none';
}

function toggleAllCodeSnippets() {
    const button = document.getElementById('collapse_all_button_code_snippets');
    const snippets = document.querySelectorAll('[id^="snippet-"]');
    const allCollapsed = Array.from(snippets).every(snippet => snippet.style.display === 'none');

    snippets.forEach(snippet => {
        snippet.style.display = allCollapsed ? 'block' : 'none';
    });

    const headers = document.querySelectorAll('.container > div > p');
    headers.forEach(header => {
        const arrow = header.textContent.slice(0, 1);
        header.textContent = (allCollapsed ? '▼' : '▶') + header.textContent.slice(1);
    });

    button.textContent = allCollapsed ? 'Collapse All' : 'Expand All';
}
"""
        ),
        Style(
            """
.collapsible-section {
    margin-bottom: 2rem;
}
.collapsible-section h5 {
    cursor: pointer;
    user-select: none;
    margin-bottom: 0.5rem;
}
.collapsible-section h5::before {
    content: '▼ ';
    font-size: 0.8em;
}
.collapsible-section h5.collapsed::before {
    content: '► ';
}
.file-explorer-collapse-btn:focus {
    outline: none;
    box-shadow: none;
}
.toggle-all-btn {
    padding: 0.125rem 0.5rem 0.125rem 0.5rem; 
    font-size: 0.75rem; 
}
#uncheck-all-btn {
    padding: 5px 10px;
}
@media (min-width: 1024px) {
    .horizontal-layout {
        display: flex;
        gap: 2rem;
    }
    .left-column {
        flex: 1;
    }
    .right-column {
        width: 50%;
    }
}
"""
        ),
    )
