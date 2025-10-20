import React, { useRef } from 'react';
import './FileUploader.css';

const FileUploader = ({ onFileSelected, acceptedTypes = 'image/*,video/*' }) => {
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      console.log('📁 Fichier sélectionné:', file.name);
      onFileSelected(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current.click();
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
  };

  const handleDragLeave = (event) => {
    event.currentTarget.classList.remove('drag-over');
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    
    const file = event.dataTransfer.files[0];
    if (file) {
      console.log('📁 Fichier déposé:', file.name);
      onFileSelected(file);
    }
  };

  return (
    <div className="file-uploader">
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedTypes}
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
      
      <div 
        className="upload-area"
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="upload-icon">📤</div>
        <h3>Charger une Image ou Vidéo</h3>
        <p>Cliquez ou glissez-déposez un fichier</p>
        <p className="supported-formats">
          Formats supportés: JPG, PNG, MP4, MOV
        </p>
      </div>
    </div>
  );
};

export default FileUploader;