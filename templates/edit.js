// 存储修改后的内容
let modifiedContent = {
    question: '',
    options: {}
};

// 在文件开头添加新的变量
let hiddenModifications = {
    question: false,
    options: {}
};

// 添加加载修改状态的函数
async function loadModifications() {
    const uuid = document.querySelector('input[name="uuid"]').value;
    const modifications = window.modifications; // 从后端传递的数据

    if (!modifications) {
        return;
    }

    // 清空当前缓存并重置状态
    modifiedContent = {
        question: '',
        options: {}
    };
    hiddenModifications = {
        question: false,
        options: {}
    };

    // 更新复选框状态和隐藏状态
    const questionCheckbox = document.querySelector('input[name="mark_question"]');
    if (questionCheckbox && questionCheckbox.checked) {
        hiddenModifications.question = true;
        // 隐藏所有修改内容
        document.querySelectorAll('.modified-content').forEach(display => {
            display.style.display = 'none';
        });
    }

    // 更新选项复选框状态和隐藏状态
    document.querySelectorAll('input[type="checkbox"][name="multiple"]').forEach((checkbox, index) => {
        if (checkbox.checked) {
            hiddenModifications.options[index] = true;
        }
    });

    // 显示修改内容并更新缓存
    if (modifications.question) {
        modifiedContent.question = modifications.question;
        updateModifiedDisplay('question', modifications.question);
        if (hiddenModifications.question) {
            const modifiedDisplay = document.querySelector('.question-text .modified-content');
            if (modifiedDisplay) {
                modifiedDisplay.style.display = 'none';
            }
        }
    }
    
    if (modifications.options) {
        // 获取原始选项数组
        const originalOptions = window.questionData.options;
        
        Object.entries(modifications.options).forEach(([originalText, newText]) => {
            // 在原始选项数组中找到对应的索引
            const index = originalOptions.findIndex(option => option === originalText);
            
            if (index !== -1) {
                modifiedContent.options[index] = newText;
                updateModifiedDisplay(`option-${index}`, newText);
                
                // 如果选项被标记删除，隐藏修改内容
                if (hiddenModifications.options[index]) {
                    const modifiedDisplay = document.querySelector(`#option-${index}-edit-area`)
                        ?.parentElement.querySelector('.modified-content');
                    if (modifiedDisplay) {
                        modifiedDisplay.style.display = 'none';
                    }
                }
            }
        });
    }
}

// 在页面加载时调用
document.addEventListener('DOMContentLoaded', loadModifications);

// 显示编辑区域
function showEditArea(id) {
    // 如果题目复选框被选中，先取消它
    const questionCheckbox = document.querySelector('input[name="mark_question"]');
    if (questionCheckbox.checked) {
        questionCheckbox.checked = false;
        hiddenModifications.question = false;
        updateAllModificationsDisplay();
    }

    // 如果是选项编辑，取消该选项的复选框
    if (id !== 'question') {
        const optionIndex = id.split('-')[1];
        const optionCheckbox = document.querySelector(`#${id}-edit-area`)
            .previousElementSibling.querySelector('input[type="checkbox"]');
        if (optionCheckbox.checked) {
            optionCheckbox.checked = false;
            hiddenModifications.options[optionIndex] = false;
            updateAllModificationsDisplay();
        }
    }
    
    document.getElementById(id + '-edit-area').style.display = 'block';
}

// 隐藏编辑区域
function hideEditArea(id) {
    document.getElementById(id + '-edit-area').style.display = 'none';
}

// 检查修改内容是否有效
function isValidModification(originalText, newText) {
    // 去除空白字符
    const trimmedNew = newText.trim();
    const trimmedOriginal = originalText.trim();
    
    // 检查是否为空
    if (trimmedNew === '') {
        alert('修改后的内容不能为空！');
        return false;
    }
    
    // 检查是否与原文完全相同
    if (trimmedNew === trimmedOriginal) {
        alert('修改后的内容与原文完全相同！');
        return false;
    }
    
    return true;
}

// 确认编辑
function confirmEdit(id) {
    const editArea = document.getElementById(id + '-edit-area');
    const editContent = editArea.querySelector('textarea').value.trim();
    const originalContent = id === 'question' 
        ? window.questionData.question 
        : window.questionData.options[parseInt(id.split('-')[1])];  // 使用完全原始的文本

    // 如果修改后的内容与原始内容相同，或者是空白内容，则不允许修改
    if (editContent === originalContent || !editContent) {
        alert('修改内容不能与原文相同或为空');
        editArea.style.display = 'none';
        return;
    }

    // 更新修改内容缓存
    if (id === 'question') {
        modifiedContent.question = editContent;
    } else {
        const optionIndex = id.split('-')[1];
        modifiedContent.options[optionIndex] = editContent;
    }

    // 更新显示
    updateModifiedDisplay(id, editContent);
    
    // 隐藏编辑区域
    editArea.style.display = 'none';
}

// 更新修改后的显示
function updateModifiedDisplay(id, content) {
    const container = id === 'question' 
        ? document.querySelector('.question-text') 
        : document.querySelector(`#${id}-edit-area`).parentElement;
    
    // 移除现有的修改显示
    const existingModified = container.querySelector('.modified-content');
    if (existingModified) {
        existingModified.remove();
    }

    // 创建新的修改显示
    const modifiedDisplay = document.createElement('div');
    modifiedDisplay.className = 'modified-content';
    
    // 创建一个内部容器来包含修改后的文本
    const contentContainer = document.createElement('div');
    contentContainer.innerHTML = '修改后: ' + content;
    modifiedDisplay.appendChild(contentContainer);
    
    // 根据当前复选框状态决定是否显示
    const questionCheckbox = document.querySelector('input[name="mark_question"]');
    const isQuestionMarked = questionCheckbox.checked;
    
    if (id === 'question') {
        modifiedDisplay.style.display = isQuestionMarked ? 'none' : 'block';
    } else {
        const optionIndex = id.split('-')[1];
        const isOptionMarked = hiddenModifications.options[optionIndex];
        modifiedDisplay.style.display = (isQuestionMarked || isOptionMarked) ? 'none' : 'block';
    }

    container.appendChild(modifiedDisplay);

    // 使用 MathJax 重新渲染数学公式
    if (window.MathJax) {
        MathJax.typesetPromise([modifiedDisplay]).catch((err) => console.log('MathJax error:', err));
    }
}

// 取消编辑
function cancelEdit(id) {
    hideEditArea(id);
}

// 重新加载修改后的内容（供后端数据更新时使用）
function reloadModifiedContent(modifiedData) {
    // 清空当前缓存
    modifiedContent = {
        question: '',
        options: {}
    };
    
    // 清除所有现有的修改显示
    document.querySelectorAll('.modified-content').forEach(el => el.remove());
    
    // 重新显示修改内容
    if (modifiedData.question) {
        modifiedContent.question = modifiedData.question;
        updateModifiedDisplay('question', modifiedData.question);
    }
    
    if (modifiedData.options) {
        Object.entries(modifiedData.options).forEach(([index, text]) => {
            modifiedContent.options[index] = text;
            updateModifiedDisplay(`option-${index}`, text);
        });
    }
}

// 修改处理复选框变化的函数
function handleCheckboxChange(type, index = null) {
    if (type === 'question') {
        // 题目复选框状态改变
        const questionCheckbox = document.querySelector('input[name="mark_question"]');
        hiddenModifications.question = questionCheckbox.checked;

        if (hiddenModifications.question) {
            // 如果题目被标记删除，取消所有选项的选中状态
            document.querySelectorAll('input[type="checkbox"][name="multiple"]').forEach((checkbox, idx) => {
                checkbox.checked = false;
                hiddenModifications.options[idx] = false;
            });
        }

        // 根据当前状态更新所有修改内容的显示
        updateAllModificationsDisplay();
    } else {
        // 如果题目复选框被选中，先取消它
        const questionCheckbox = document.querySelector('input[name="mark_question"]');
        if (questionCheckbox.checked) {
            questionCheckbox.checked = false;
            hiddenModifications.question = false;
        }

        // 然后处理选项复选框的变化
        const optionCheckbox = document.querySelector(`#option-${index}-edit-area`)
            .previousElementSibling.querySelector('input[type="checkbox"]');
        hiddenModifications.options[index] = optionCheckbox.checked;
        
        // 更新所有修改内容的显示
        updateAllModificationsDisplay();
    }
}

// 更新所有修改内容的显示状态
function updateAllModificationsDisplay() {
    const questionCheckbox = document.querySelector('input[name="mark_question"]');
    const isQuestionMarked = questionCheckbox.checked;

    // 更新问题的修改显示
    const questionModified = document.querySelector('.question-text .modified-content');
    if (questionModified) {
        questionModified.style.display = isQuestionMarked ? 'none' : 'block';
    }

    // 更新所有选项的修改显示
    Object.keys(modifiedContent.options).forEach(index => {
        const modifiedDisplay = document.querySelector(`#option-${index}-edit-area`)
            ?.parentElement.querySelector('.modified-content');
        if (modifiedDisplay) {
            // 只有当题目和选项都没有被标记删除时才显示修改
            const isOptionMarked = hiddenModifications.options[index];
            const shouldShow = !isQuestionMarked && !isOptionMarked;
            modifiedDisplay.style.display = shouldShow ? 'block' : 'none';
        }
    });
}

// 修改表单提交处理函数
document.getElementById('submit-form').addEventListener('submit', function(e) {
    // 如果题目没有被标记删除，检查剩余选项数量
    const questionCheckbox = document.querySelector('input[name="mark_question"]');
    const optionCheckboxes = Array.from(document.querySelectorAll('input[type="checkbox"][name="multiple"]'));
    
    if (!questionCheckbox.checked) {
        const remainingOptions = optionCheckboxes.filter(checkbox => !checkbox.checked).length;
        // if (remainingOptions < 4) {
        //     e.preventDefault();
        //     alert('一个题目的选项至少应为4个，请通过修改选项来补充选项至少为4个');
        //     return;
        // }
    }

    // 如果有修改内容，添加到表单中
    if (Object.keys(modifiedContent.options).length > 0 || modifiedContent.question) {
        // 如果题目被标记删除，不发送任何修改
        if (hiddenModifications.question) {
            return;
        }

        // 过滤掉被标记删除的选项的修改
        const finalModifications = {
            question: modifiedContent.question,
            options: {}
        };
        
        // 从原始数据中获取选项文本，使用完全原始的文本作为键
        const originalOptions = window.questionData.options;
        
        Object.entries(modifiedContent.options).forEach(([index, text]) => {
            if (!hiddenModifications.options[index]) {
                const originalText = originalOptions[parseInt(index)];
                
                if (!originalText) {
                    console.error('Failed to get original text for option:', index);
                    return;
                }
                
                // 直接使用原始文本作为键，不做任何修改
                finalModifications.options[originalText] = text;
            }
        });

        const modifiedContentInput = document.createElement('input');
        modifiedContentInput.type = 'hidden';
        modifiedContentInput.name = 'modified_content';
        modifiedContentInput.value = JSON.stringify(finalModifications);
        this.appendChild(modifiedContentInput);
    }
});

// 添加展开/收起响应内容的函数
function toggleResponse(button) {
    const content = button.previousElementSibling;
    const isCollapsed = content.classList.contains('collapsed');
    
    content.classList.toggle('collapsed');
    button.textContent = isCollapsed ? '收起' : '展开';
    
    if (!isCollapsed) {
        // 滚动到按钮位置，确保用户看到收起按钮
        button.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
} 