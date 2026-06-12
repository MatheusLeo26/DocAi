import sys

JS_CODE = """            let selectedFiles = [];
            let selectedFile = null;

            // Drag and drop events for dropzone
            ['dragenter', 'dragover'].forEach(eventName => {
                dropzone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    dropzone.classList.add('dragover');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    dropzone.classList.remove('dragover');
                }, false);
            });

            dropzone.addEventListener('drop', (e) => {
                const dt = e.dataTransfer;
                if (dt.files.length > 0) {
                    handleFileSelect(dt.files);
                }
            });

            dropzone.addEventListener('click', () => fileInput.click());
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    handleFileSelect(e.target.files);
                }
            });

            removeFileBtn.addEventListener('click', () => {
                selectedFiles = [];
                selectedFile = null;
                fileInput.value = '';
                fileInfo.classList.remove('show');
                dropzone.style.display = 'block';
                formatGroup.style.display = 'none';
                document.getElementById('compressOptions').style.display = 'none';
                document.getElementById('splitOptions').style.display = 'none';
                convertBtn.disabled = true;
                convertBtn.textContent = 'Converter e Baixar';
            });

            targetFormat.addEventListener('change', () => {
                const val = targetFormat.value;
                document.getElementById('compressOptions').style.display = val === 'compress' ? 'block' : 'none';
                document.getElementById('splitOptions').style.display = val === 'split' ? 'block' : 'none';
                
                if (val === 'reorder') {
                    convertBtn.textContent = 'Organizar Páginas';
                } else if (val === 'merge') {
                    convertBtn.textContent = 'Mesclar e Organizar';
                } else if (val === 'split') {
                    convertBtn.textContent = 'Dividir PDF';
                } else if (val === 'compress') {
                    convertBtn.textContent = 'Comprimir PDF';
                } else {
                    convertBtn.textContent = 'Converter e Baixar';
                }
            });
            
            document.getElementById('splitMode').addEventListener('change', (e) => {
                document.getElementById('splitRangeContainer').style.display = e.target.value === 'interval' ? 'block' : 'none';
            });

            let draggedCard = null;

            function setupDragAndDrop(card) {
                card.addEventListener('dragstart', function(e) {
                    draggedCard = this;
                    setTimeout(() => this.classList.add('dragging'), 0);
                });

                card.addEventListener('dragend', function(e) {
                    draggedCard = null;
                    this.classList.remove('dragging');
                });

                card.addEventListener('dragover', function(e) {
                    e.preventDefault();
                });

                card.addEventListener('dragenter', function(e) {
                    e.preventDefault();
                    if (this !== draggedCard && draggedCard) {
                        const grid = document.getElementById('pagesGrid');
                        const cards = Array.from(grid.querySelectorAll('.page-card'));
                        const draggedIndex = cards.indexOf(draggedCard);
                        const targetIndex = cards.indexOf(this);
                        
                        if (draggedIndex < targetIndex) {
                            this.parentNode.insertBefore(draggedCard, this.nextSibling);
                        } else {
                            this.parentNode.insertBefore(draggedCard, this);
                        }
                    }
                });
            }

            function handleFileSelect(files) {
                selectedFiles = Array.from(files);
                if (selectedFiles.length === 0) return;
                
                selectedFile = selectedFiles[0];
                fileInfo.classList.add('show');
                dropzone.style.display = 'none';
                convertBtn.disabled = false;
                convertBtn.textContent = 'Converter e Baixar';
                document.getElementById('compressOptions').style.display = 'none';
                document.getElementById('splitOptions').style.display = 'none';
                
                targetFormat.innerHTML = '';

                if (selectedFiles.length > 1) {
                    // Check if all are PDFs
                    const allPdfs = selectedFiles.every(f => f.name.toLowerCase().endsWith('.pdf'));
                    if (allPdfs) {
                        document.getElementById('fileName').textContent = `${selectedFiles.length} arquivos selecionados`;
                        document.getElementById('fileSize').textContent = 'Vários arquivos PDF';
                        formatGroup.style.display = 'block';
                        targetFormat.innerHTML = `<option value="merge">Juntar PDFs</option>`;
                        convertBtn.textContent = 'Mesclar e Organizar';
                    } else {
                        alert('Para mesclar, todos os arquivos devem ser PDF.');
                        removeFileBtn.click();
                    }
                    return;
                }

                fileName.textContent = selectedFile.name;
                fileSize.textContent = (selectedFile.size / (1024 * 1024)).toFixed(2) + ' MB';
                const ext = selectedFile.name.split('.').pop().toLowerCase();

                if (ext === 'docx') {
                    formatGroup.style.display = 'block';
                    targetFormat.innerHTML = '<option value="pdf">PDF</option>';
                } else if (ext === 'pdf') {
                    formatGroup.style.display = 'block';
                    targetFormat.innerHTML = `
                        <option value="pdfa">PDF/A</option>
                        <option value="compress">Comprimir PDF</option>
                        <option value="split">Dividir PDF</option>
                        <option value="reorder">Reorganizar Páginas</option>
                    `;
                } else if (['png', 'jpg', 'jpeg', 'jfif'].includes(ext)) {
                    formatGroup.style.display = 'block';
                    const options = ['PNG', 'JPG', 'JFIF'].filter(f => f.toLowerCase() !== ext && !(ext === 'jpeg' && f === 'JPG'));
                    targetFormat.innerHTML = options.map(opt => `<option value="${opt.toLowerCase()}">${opt}</option>`).join('');
                } else {
                    formatGroup.style.display = 'none';
                    alert('Formato não suportado. Por favor selecione um arquivo válido.');
                    removeFileBtn.click();
                }
            }

            async function openOrganizerWorkspace(pdfFile) {
                loadingOverlay.querySelector('.loading-text').textContent = 'Preparando páginas do PDF...';
                loadingOverlay.classList.add('show');
                
                const reader = new FileReader();
                reader.onload = async function() {
                    const arrayBuffer = this.result;
                    try {
                        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';
                        const pdf = await pdfjsLib.getDocument({data: arrayBuffer}).promise;
                        const numPages = pdf.numPages;
                        const pagesGrid = document.getElementById('pagesGrid');
                        pagesGrid.innerHTML = '';
                        
                        for (let i = 1; i <= numPages; i++) {
                            const page = await pdf.getPage(i);
                            const viewport = page.getViewport({scale: 0.3});
                            const canvas = document.createElement('canvas');
                            const context = canvas.getContext('2d');
                            canvas.height = viewport.height;
                            canvas.width = viewport.width;
                            
                            await page.render({
                                canvasContext: context,
                                viewport: viewport
                            }).promise;
                            
                            const card = document.createElement('div');
                            card.className = 'page-card';
                            card.draggable = true;
                            card.dataset.index = i - 1; // 0-based index
                            
                            const badge = document.createElement('div');
                            badge.className = 'page-badge';
                            badge.textContent = `Página ${i}`;
                            
                            card.appendChild(canvas);
                            card.appendChild(badge);
                            pagesGrid.appendChild(card);
                            
                            setupDragAndDrop(card);
                        }
                        
                        // Always keep reference to the final pdf being edited
                        selectedFile = pdfFile;
                        
                        document.querySelector('.converter-box').style.display = 'none';
                        document.getElementById('organizerWorkspace').classList.add('show');
                        loadingOverlay.classList.remove('show');
                    } catch (err) {
                        loadingOverlay.classList.remove('show');
                        alert('Erro ao processar o arquivo PDF: ' + err.message);
                    }
                };
                reader.readAsArrayBuffer(pdfFile);
            }

            convertForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                if (selectedFiles.length === 0) return;

                const targetVal = targetFormat.value;
                
                if (targetVal === 'merge') {
                    const formData = new FormData();
                    selectedFiles.forEach(f => formData.append('files', f));
                    
                    loadingOverlay.querySelector('.loading-text').textContent = 'Mesclando arquivos...';
                    loadingOverlay.classList.add('show');
                    
                    try {
                        const res = await authFetch('/api/convert/merge-pdfs', {
                            method: 'POST',
                            body: formData
                        });
                        if (res.ok) {
                            const blob = await res.blob();
                            // Create a file object from blob so we can load it into organizer
                            const mergedFile = new File([blob], "merged_pdfs.pdf", { type: "application/pdf" });
                            loadingOverlay.classList.remove('show');
                            // Open organizer
                            openOrganizerWorkspace(mergedFile);
                        } else {
                            loadingOverlay.classList.remove('show');
                            const err = await res.json();
                            alert(err.message || 'Erro ao mesclar arquivos');
                        }
                    } catch (err) {
                        loadingOverlay.classList.remove('show');
                        alert('Erro na conexão: ' + err.message);
                    }
                    return;
                }

                if (targetVal === 'reorder') {
                    openOrganizerWorkspace(selectedFile);
                    return;
                }

                const formData = new FormData();
                formData.append('file', selectedFile);

                let endpoint = '';
                const ext = selectedFile.name.split('.').pop().toLowerCase();
                let downloadExt = ext;
                let suffix = '';

                if (ext === 'docx') {
                    endpoint = '/api/convert/document';
                    downloadExt = 'pdf';
                } else if (ext === 'pdf') {
                    if (targetVal === 'pdfa') {
                        endpoint = '/api/convert/pdf';
                        suffix = '_pdfa';
                    } else if (targetVal === 'compress') {
                        endpoint = '/api/convert/compress-pdf';
                        formData.append('level', document.getElementById('compressLevel').value);
                        suffix = '_comprimido';
                    } else if (targetVal === 'split') {
                        endpoint = '/api/convert/split-pdf';
                        const splitMode = document.getElementById('splitMode').value;
                        formData.append('mode', splitMode);
                        if (splitMode === 'interval') {
                            formData.append('range', document.getElementById('splitRange').value);
                            suffix = '_intervalo';
                        } else {
                            downloadExt = 'zip';
                            suffix = '_dividido';
                        }
                    }
                } else {
                    endpoint = '/api/convert/image';
                    formData.append('target_format', targetVal);
                    downloadExt = targetVal;
                }

                loadingOverlay.querySelector('.loading-text').textContent = 'Processando...';
                loadingOverlay.classList.add('show');

                try {
                    const res = await authFetch(endpoint, {
                        method: 'POST',
                        body: formData
                    });

                    loadingOverlay.classList.remove('show');
                    if (!res) return;

                    if (res.ok) {
                        const blob = await res.blob();
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        const baseName = selectedFile.name.substring(0, selectedFile.name.lastIndexOf('.'));
                        a.download = `${baseName}${suffix}.${downloadExt}`;
                        a.click();
                    } else {
                        const err = await res.json();
                        alert(err.message || 'Erro no processamento');
                    }
                } catch (err) {
                    loadingOverlay.classList.remove('show');
                    alert('Erro na conexão: ' + err.message);
                }
            });

            // Cancel and Save buttons for Organizer
            document.getElementById('cancelOrganizeBtn').addEventListener('click', () => {
                document.getElementById('organizerWorkspace').classList.remove('show');
                document.querySelector('.converter-box').style.display = 'block';
                // Only reset if single file
                if (selectedFiles.length === 1) {
                    targetFormat.value = 'pdfa';
                    convertBtn.textContent = 'Converter e Baixar';
                    document.getElementById('compressOptions').style.display = 'none';
                    document.getElementById('splitOptions').style.display = 'none';
                }
            });

            document.getElementById('saveOrganizeBtn').addEventListener('click', async () => {
                if (!selectedFile) return;
                
                const cards = document.querySelectorAll('.page-card');
                const pageOrder = Array.from(cards).map(card => parseInt(card.dataset.index));
                
                const formData = new FormData();
                formData.append('file', selectedFile);
                formData.append('page_order', JSON.stringify(pageOrder));
                
                loadingOverlay.querySelector('.loading-text').textContent = 'Reorganizando páginas e gerando o novo PDF...';
                loadingOverlay.classList.add('show');
                
                try {
                    const res = await authFetch('/api/convert/reorder-pdf', {
                        method: 'POST',
                        body: formData
                    });
                    
                    loadingOverlay.classList.remove('show');
                    
                    if (!res) return;
                    
                    if (res.ok) {
                        const blob = await res.blob();
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        let baseName = selectedFile.name;
                        if (baseName.endsWith('.pdf')) baseName = baseName.substring(0, baseName.lastIndexOf('.'));
                        a.download = `${baseName}_final.pdf`;
                        a.click();
                        
                        // Close workspace
                        document.getElementById('cancelOrganizeBtn').click();
                    } else {
                        const err = await res.json();
                        alert(err.message || 'Erro ao organizar páginas');
                    }
                } catch (err) {
                    loadingOverlay.classList.remove('show');
                    alert('Erro na conexão: ' + err.message);
                }
            });
        });
    </script>
</body>
</html>"""

import re
filepath = r"c:\Users\SrgRH\.gemini\antigravity-ide\scratch\pdf_generator_app\templates\converter.html"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace from `            // Drag and drop events for dropzone` to end of file
start_marker = "            // Drag and drop events for dropzone"
idx = content.find(start_marker)

# Because we also need to replace `let selectedFile = null;` which is just before it:
prefix = content[:content.rfind("let selectedFile = null;", 0, idx)]
new_content = prefix + JS_CODE

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)
    
print("Successfully updated converter.html")
