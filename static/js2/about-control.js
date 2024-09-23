function validateAndPostSaran() {
  const name = document.getElementById('username').value.trim();
  const message = document.getElementById('message').value.trim();

  if (name === '') {
      Swal.fire('Error', 'Nama harus diisi!', 'error');
      return;
  }

  if (message === '') {
      Swal.fire('Error', 'Saran atau masukan harus diisi!', 'error');
      return;
  }

  // Jika validasi berhasil, panggil fungsi untuk mengirimkan saran
  postsaran(name, message);
}

function postsaran() {
    let username = $("#username").val();
    let message = $("#message").val();
    $.ajax({
      type: "POST",
      url: "/post_saran",
      data: {
        username_give: username,
        message_give: message,
      },
      success: function (response) {
        if (response["result"] === "success") {
          alert(response["msg"]);
          $("#username").val("");
          $("#message").val("");
        }
      },
    });
  }