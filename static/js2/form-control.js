function openregister(){
    $('#regform').toggleClass("visually-hidden");
    $('#add-regform').toggleClass("visually-hidden");
    $('#add-logform').addClass("visually-hidden");
    $('#title-login').addClass("visually-hidden");
}

function openlogin(){
    $('#regform').addClass("visually-hidden");
    $('#add-regform').addClass("visually-hidden");
    $('#add-logform').toggleClass("visually-hidden");
    $('#title-login').toggleClass("visually-hidden");
}

function showpassword(){
    let password = $('#form-password')
    password.setAttribute("type", "text");
}

const togglePassword = document.querySelector("#togglePassword");
const password = document.querySelector("#form-password");

togglePassword.addEventListener("click", function () {
    // toggle the type attribute
    const type = password.getAttribute("type") === "password" ? "text" : "password";
    password.setAttribute("type", type);
    
    // toggle the icon
    this.classList.toggle("bi-eye");
});

function showhidePass (){

const togglePassword2 = document.querySelector("#togglePassword2");
const password2 = document.querySelector("#form-password2");

togglePassword2.addEventListener("click", function () {
    // toggle the type attribute
    const type = password2.getAttribute("type") === "password" ? "text" : "password";
    password2.setAttribute("type", type);
    
    // toggle the icon
    this.classList.toggle("bi-eye");
});
}

showhidePass();

function is_password(asValue) {
    var regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,20}$/;
    return regExp.test(asValue);
}

function is_email(asValue) {
    var regExp = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
    return regExp.test(asValue);
}

function login(){
    let inputEmail = $('#form-email');
    let inputPassword = $('#form-password');

    let email = inputEmail.val();
    let password = inputPassword.val();
    let hashpassword = '';

    let helpEmail = $('#help-email');
    let helpPassword = $('#help-password');

    if (email === "") {
      $('#fg-email')
      .removeClass('mb-3')
      .addClass('mb-1')
      helpEmail
        .text("Mohon masukkan email!")
        .removeClass("text-dark")
        .addClass("text-danger");
      inputEmail.focus();
      return;
    } else if (!is_email(email)) {
      $('#fg-email')
      .removeClass('mb-3')
      .addClass('mb-1')
      helpEmail
        .text(
          "Masukkan email dengan benar (example@example.com)"
        )
        .removeClass("text-dark")
        .addClass("taxt-danger");
      inputEmail.focus();
    } else {
      $('#fg-email')
      .removeClass('mb-3')
      .addClass('mb-1')
      helpEmail
        .text("Email sesuai!")
        .removeClass("text-danger")
        .removeClass("text-dark")
        .addClass("text-success");
    }

    if (password === "") {
      helpPassword
        .text("Mohon masukkan password!")
        .removeClass("text-dark")
        .addClass("text-danger");
      inputPassword.focus();
      return;
    } else {
      helpPassword
        .text("Password sesuai!")
        .removeClass("text-danger")
        .removeClass("text-dark")
        .addClass("text-success");
      hashpassword= sha256(password);
    }

    $.ajax({
      type: "POST",
      url: "/login",
      data: {
        email_give: email,
        password_give: hashpassword,
      },
      success: function (response) {
        if (response["result"] == "success") {
          if(!response.data['blocked']){
          $.cookie("mytoken", response["token"], { path: "/" });
          if(response.data['level'] === 2){
            Swal.fire({
              title: "Berhasil login",
              text: "Anda berhasil login!" + response.data['profilename'],
              icon: "success"
            }).then((result) => {
            if (result.isConfirmed) {
              window.location.href = "/";
              }
            })
          }else if(response.data['level'] === 1){
            Swal.fire({
              title: "Berhasil login",
              text: "Anda berhasil login!",
              icon: "success"
            }).then((result) => {
  /* Read more about isConfirmed, isDenied below */
            if (result.isConfirmed) {
              window.location.href = "/dashboard";
              }
            })
            
          }
        }
        } else if(response["result"] == "fail") {
          if(response["status"] == "block"){
            Swal.fire({
            title: "Gagal login",
            showDenyButton: true,
            showCancelButton: false,
            confirmButtonText: "Kirim Permintaan",
            denyButtonText: "Tutup",
            html: `
            <h4 class="text-danger">Akun anda telah terblokir!</h4>
            <p>Alasan Pemblokiran: ${response.data['reasonblock']}<p>
            <small class="text-danger">Hubungi admin untuk informasi lebih lanjut dengan mengirim permintaan melalui tombol di bawah</small>
          `,
            icon: "error"
          }).then((result) => {
            /* Read more about isConfirmed, isDenied below */
            if (result.isConfirmed) {
              window.location.href = "/about?user="+response.data['userblock']+"&request=req#msgFormBox"
            } else if (result.isDenied) {
              Swal.DismissReason.cancel;
            }
          });;
          resetform_login()
          }else{
          Swal.fire({
            title: "Gagal login",
            text: response["msg"],
            icon: "error"
          })
          $('#form-email').val('');
          $('#form-password').val('');
          }
        }

      },
    });

}

function resetform_login(){
    $('#form-email').val('');
    $('#form-password').val('');
}

function check_dup(){
    let inputUsername = $('#form-username');
    let username = inputUsername.val();
    let helpUsername = $('#help-username')

    if (username === "") {
        $('#fg-username')
            .removeClass('mb-3')
            .addClass('mb-1')
        helpUsername
          .text("Mohon masukkan username!")
          .addClass("text-danger");
        inputUsername.focus();
        return;
      }

      $.ajax({
        type: "POST",
        url: "/register/check_dup",
        data: {
          username_give: username,
        },
        success: function (response) {
          if (response["exists"]) {
            helpUsername
              .text("Username sudah digunakan!")
              .removeClass("text-dark")
              .addClass("text-danger");
            $("#input-username").focus();
          } else {
            $('#fg-username')
            .removeClass('mb-3')
            .addClass('mb-1')
            helpUsername
              .text("Username dapat digunakan!")
              .removeClass("text-danger")
              .addClass("text-success");
          }
        },
      });
}

function register(){
    let inputUsername = $('#form-username');
    let inputEmail = $('#form-email');
    let inputPassword = $('#form-password');
    let inputPassword2 = $('#form-password2');
    
    let username = inputUsername.val();
    let email = inputEmail.val();
    let password = inputPassword.val();
    let password2 = inputPassword2.val();
    let hashpassword = '';

    let helpUsername = $('#help-username');
    let helpEmail = $('#help-email');
    let helpPassword = $('#help-password');
    let helpPassword2 = $('#help-password2');


    if (helpUsername.hasClass("text-danger")) {
      alert("Mohon cek username anda!");
      return;
    } else if (!helpUsername.hasClass("text-success")) {
      alert("Mohon cek ulang username anda!");
      return;
    }

    if (email === "") {
        $('#fg-email')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpEmail
          .text("Mohon masukkan email!")
          .removeClass("text-dark")
          .addClass("text-danger");
        inputEmail.focus();
        return;
      } else if (!is_email(email)) {
        $('#fg-email')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpEmail
          .text(
            "Masukkan email dengan benar (example@example.com)"
          )
          .removeClass("text-dark")
          .addClass("taxt-danger");
        inputEmail.focus();
      } else {
        $('#fg-email')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpEmail
          .text("Email dapat digunakan!")
          .removeClass("text-danger")
          .removeClass("text-dark")
          .addClass("text-success");
      }

    if (password === "") {
        helpPassword
          .text("Mohon masukkan password!")
          .removeClass("text-dark")
          .addClass("text-danger");
        inputPassword.focus();
        return;
      } else if (!is_password(password)) {
        helpPassword
          .text(
            "Masukkan password dengan 8-10 karakter, angka, atau spesial karakter (!@#$%^&*)"
          )
          .removeClass("text-dark")
          .addClass("taxt-danger");
        inputPassword.focus();
      } else {
        helpPassword
          .text("Password dapat digunakan!")
          .removeClass("text-danger")
          .removeClass("text-dark")
          .addClass("text-success");
      }

    if (password2 === ""){
        $('#fg-password2')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpPassword2
        .text(
          "Masukkan ulang password!"
        )
        .removeClass("text-dark")
        .addClass("taxt-danger");
      inputPassword2.focus();
      } else if (password2 !== password){
        $('#fg-password2')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpPassword2
        .text(
          "Masukkan password yang sama dengan sebelumnya!"
        )
        .removeClass("text-dark")
        .addClass("taxt-danger");
      inputPassword2.focus();
    } else {
        helpPassword2
        .text("Password sesuai!")
        .removeClass("text-danger")
        .removeClass("text-dark")
        .addClass("text-success");
      
        hashpassword = sha256(password);

        $.ajax({
          type: "POST",
          url: "/register",
          data: {
            username_give: username,
            email_give: email,
            password_give: hashpassword,
          },
          success: function (response) {
            console.log(response.data);
            if(response['result']==='success'){
            Swal.fire({
              title: "Berhasil register",
              text: "Akun anda telah terdaftar! Silakan login",
              icon: "success"
            }).then((result) => {
            if (result.isConfirmed) {
              window.location.replace("/login?email="+response.data);
              }
            })
          }else if(response['result']==='fail'){
            Swal.fire({
              title: "Gagal register",
              text: response["msg"],
              icon: "error"
            })
            $('#form-email').val('');
            $('#form-password').val('');
            $('#form-password2').val('');
          }
        }
    })
}
}

function resetform_register(){
    $('#form-email').val('');
    $('#form-password').val('');
}