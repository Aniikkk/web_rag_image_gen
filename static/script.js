document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('generate-form');
    const generateBtn = document.getElementById('generate-btn');
    const status = document.getElementById('status');
    const logOutput = document.getElementById('log-output');
    const imageResult = document.getElementById('image-result');
    const generatedImage = document.getElementById('generated-image');

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get form data
        const prompt = document.getElementById('prompt').value;
        const numImages = document.getElementById('num-images').value;
        
        // Disable button during processing
        generateBtn.disabled = true;
        
        // Clear previous outputs
        logOutput.textContent = '';
        generatedImage.innerHTML = '';
        imageResult.classList.add('hidden');
        
        // Update status
        status.textContent = 'Generating image...';
        status.style.color = '';
        status.style.backgroundColor = '';
        
        try {
            // Create EventSource for server-sent events
            const eventSource = new EventSource(`/generate?prompt=${encodeURIComponent(prompt)}&num_images=${numImages}`);
            
            // Handle log messages
            eventSource.addEventListener('log', function(event) {
                const data = JSON.parse(event.data);
                logOutput.textContent += data.message + '\n';
                // Auto-scroll to bottom
                logOutput.scrollTop = logOutput.scrollHeight;
            });
            
            // Handle completion event
            eventSource.addEventListener('complete', function(event) {
                const data = JSON.parse(event.data);
                
                if (data.success) {
                    // Update status
                    status.textContent = 'Image generation complete!';
                    status.style.color = 'white';
                    status.style.backgroundColor = '#27ae60';
                    
                    // Display the generated image
                    imageResult.classList.remove('hidden');
                    const img = document.createElement('img');
                    img.src = data.image_path;
                    img.alt = 'Generated image';
                    generatedImage.appendChild(img);
                } else {
                    // Handle error
                    status.textContent = 'Error: ' + data.error;
                    status.style.color = 'white';
                    status.style.backgroundColor = '#e74c3c';
                    
                    // Display error message in the results area
                    imageResult.classList.remove('hidden');
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    errorDiv.innerHTML = `
                        <h3>Error</h3>
                        <p>${data.error}</p>
                        <p>Please try a different prompt or adjust the number of images.</p>
                    `;
                    generatedImage.appendChild(errorDiv);
                }
                
                // Close the event source
                eventSource.close();
                
                // Re-enable the button
                generateBtn.disabled = false;
            });
            
            // Handle errors
            eventSource.onerror = function() {
                status.textContent = 'Connection error. Please try again.';
                status.style.color = 'white';
                status.style.backgroundColor = '#e74c3c';
                eventSource.close();
                generateBtn.disabled = false;
            };
            
        } catch (error) {
            console.error('Error:', error);
            status.textContent = 'Error: ' + error.message;
            status.style.color = 'white';
            status.style.backgroundColor = '#e74c3c';
            generateBtn.disabled = false;
        }
    });
}); 