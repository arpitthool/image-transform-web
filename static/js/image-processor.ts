// TypeScript interfaces for type safety
interface ImageProcessorElements {
    grayscaleBtn: HTMLButtonElement;
    loading: HTMLElement;
    processedContainer: HTMLElement;
}

interface ProcessResponse {
    ok: boolean;
    blob(): Promise<Blob>;
    text(): Promise<string>;
}

class ImageProcessor {
    private filename: string;
    private elements: ImageProcessorElements;

    constructor(filename: string) {
        this.filename = filename;
        this.elements = this.initializeElements();
        this.attachEventListeners();
    }

    private initializeElements(): ImageProcessorElements {
        const grayscaleBtn = document.getElementById('grayscaleBtn') as HTMLButtonElement;
        const loading = document.getElementById('loading') as HTMLElement;
        const processedContainer = document.getElementById('processedImageContainer') as HTMLElement;

        if (!grayscaleBtn || !loading || !processedContainer) {
            throw new Error('Required DOM elements not found');
        }

        return { grayscaleBtn, loading, processedContainer };
    }

    private attachEventListeners(): void {
        this.elements.grayscaleBtn.addEventListener('click', () => this.handleGrayscaleConversion());
    }

    private async handleGrayscaleConversion(): Promise<void> {
        // Show loading state
        this.elements.grayscaleBtn.disabled = true;
        this.elements.loading.style.display = 'block';

        try {
            await this.processImage();
        } catch (error) {
            this.handleError(error);
        } finally {
            // Hide loading state
            this.elements.grayscaleBtn.disabled = false;
            this.elements.loading.style.display = 'none';
        }
    }

    private async processImage(): Promise<void> {
        // Create FormData with the original image file
        const formData = new FormData();

        // Fetch the original image as a blob
        const response = await fetch(`/uploads/${this.filename}`);
        const blob = await response.blob();

        // Create a file from the blob
        const file = new File([blob], this.filename, { type: blob.type });
        formData.append('file', file);

        // Send request to grayscale API
        const processResponse = await fetch('/image/transform/grayscale', {
            method: 'POST',
            body: formData
        }) as ProcessResponse;

        if (processResponse.ok) {
            await this.displayProcessedImage(processResponse);
        } else {
            await this.handleApiError(processResponse);
        }
    }

    private async displayProcessedImage(response: ProcessResponse): Promise<void> {
        // Convert response to blob
        const processedBlob = await response.blob();

        // Create image element and display
        const img = document.createElement('img');
        img.src = URL.createObjectURL(processedBlob);
        img.alt = 'Processed Image';
        img.className = 'uploaded-image';

        // Clear container and add image
        this.elements.processedContainer.innerHTML = '';
        this.elements.processedContainer.appendChild(img);
    }

    private async handleApiError(response: ProcessResponse): Promise<void> {
        const errorText = await response.text();
        this.elements.processedContainer.innerHTML = `<p style="color: red;">Error: ${errorText}</p>`;
    }

    private handleError(error: unknown): void {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        this.elements.processedContainer.innerHTML = `<p style="color: red;">Network error: ${errorMessage}</p>`;
    }
}

// Initialize the image processor when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Get the filename from the data attribute or global variable
    const filenameElement = document.querySelector('[data-filename]') as HTMLElement;
    const filename = filenameElement?.dataset.filename || (window as any).filename;
    
    if (!filename) {
        console.error('Filename not found');
        return;
    }

    new ImageProcessor(filename);
});
