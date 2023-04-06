function deleteNote(noteId) {
    fetch("/delete-note", {
      method: "POST",
      body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }
  function deleteText(textId) {
    fetch("/delete-text", {
      method: "POST",
      body: JSON.stringify({ textId: textId }),
    }).then((_res) => {
      window.location.href = "/";
    });
  }