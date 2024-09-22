const togglePasswordOld = document.querySelector("#togglePasswordOld");
const passwordOld = document.querySelector("#old-password");

togglePasswordOld.addEventListener("click", function () {
// toggle the type attribute
const type = passwordOld.getAttribute("type") === "password" ? "text" : "password";
passwordOld.setAttribute("type", type);

// toggle the icon
this.classList.toggle("bi-eye");
});

const togglePasswordNew = document.querySelector("#togglePasswordNew");
const passwordNew = document.querySelector("#new-password");

togglePasswordNew.addEventListener("click", function () {
// toggle the type attribute
const type = passwordNew.getAttribute("type") === "password" ? "text" : "password";
passwordNew.setAttribute("type", type);

// toggle the icon
this.classList.toggle("bi-eye");
});

function is_password(asValue) {
    var regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,20}$/;
    return regExp.test(asValue);
}

function is_email(asValue) {
    var regExp = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;
    return regExp.test(asValue);
}

function is_phone(asValue) {
    var regExp = /^\+62[0-9]{10,12}$/;
    return regExp.test(asValue);
}

function update_profile(){
    let inputFullname = $('#fullname');
    let inputEmail = $('#email');
    let inputJob = $('#job');
    let inputPhone = $('#mobile');
    let inputAddress = $('#address');
    let inputBio = $('#bio');
    
    let fullname = inputFullname.val();
    let email = inputEmail.val();
    let job = inputJob.val();
    let phone = inputPhone.val();
    let address = inputAddress.val();
    let bio = inputBio.val();
    let file = $("#image")[0].files[0];

    let helpFullname = $('#help-fullname');
    let helpEmail = $('#help-email');
    let helpJob = $('#help-job');
    let helpPhone = $('#help-phone');
    let helpAddress = $('#help-address');
    let helpBio = $('#help-bio');


    if (fullname === "") {
        $('#fg-fullname')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpFullname
          .text("Mohon masukkan nama lengkap anda!")
          .removeClass("text-dark")
          .addClass("text-danger");
        inputFullname.focus();
        return;
      } else {
        $('#fg-fullname')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpEmail
          .text("Full Name sesuai!")
          .removeClass("text-danger")
          .removeClass("text-dark")
          .addClass("text-success");
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

    if (job === "") {
        $('#fg-job')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpJob
          .text("Mohon masukkan Pekerjaan anda dengan benar!")
          .removeClass("text-dark")
          .addClass("text-danger");
        inputJob.focus();
        return;
      } else {
        $('#fg-job')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpJob
          .text("Isian pekerjaan sesuai!")
          .removeClass("text-danger")
          .removeClass("text-dark")
          .addClass("text-success");
      }

      if (phone === "") {
        $('#fg-phone')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpPhone
          .text("Mohon masukkan nomor anda dengan benar!")
          .removeClass("text-dark")
          .addClass("text-danger");
        inputPhone.focus();
        return;
      } else if (!is_phone(phone)){
        $('#fg-phone')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpPhone
          .text(
            "Masukkan nomor telepon antara 11-13 digit dan diawali dengan +62"
          )
          .removeClass("text-dark")
          .addClass("taxt-danger");
        inputPhone.focus();
      } else {
        $('#fg-phone')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpPhone
          .text("Nomor sesuai!")
          .removeClass("text-danger")
          .removeClass("text-dark")
          .addClass("text-success");
      }

      if (address === "") {
        $('#fg-address')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpAddress
          .text("Mohon masukkan alamat anda dengan benar!")
          .removeClass("text-dark")
          .addClass("text-danger");
        inputAddress.focus();
        return;
      } else {
        $('#fg-address')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpAddress
          .text("Isian alamat sesuai!")
          .removeClass("text-danger")
          .removeClass("text-dark")
          .addClass("text-success");
      }

      if (bio === "") {
        $('#fg-bio')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpBio
          .text("Mohon masukkan bio profil anda dengan benar!")
          .removeClass("text-dark")
          .addClass("text-danger");
        inputBio.focus();
        return;
      } else {
        $('#fg-bio')
        .removeClass('mb-3')
        .addClass('mb-1')
        helpBio
          .text("Isian bio sesuai!")
          .removeClass("text-danger")
          .removeClass("text-dark")
          .addClass("text-success");
      }

let form_data = new FormData();
    form_data.append("file_give", file);
    form_data.append("fullname_give", fullname);
    form_data.append("email_give", email);
    form_data.append("job_give", job);
    form_data.append("phone_give", phone);
    form_data.append("address_give", address);
    form_data.append("bio_give", bio);

console.log(form_data)
    
$.ajax({
  type: "POST",
  url: "/update_profile",
  data: form_data,
  cache: false,
  contentType: false,
  processData: false,
  success: function (response) {
    if(response['result'] ==='success'){
    alert("Profil akun anda berhasil diupdate!");
    window.location.reload();
    }
  },
});      
}

function resetPass(username, password){
  let passOldInput = $('#old-password');
  let passNewInput = $('#new-password');

  let passOld = passOldInput.val();
  let passNew = passNewInput.val();

  let hashOld = sha256(passOld);
  let hashNew = sha256(passNew);

  if(passNew === ''){
    alert('Mohon masukkan password baru!')
    passNewInput.val("");
    passNewInput.focus();
  }else if(!is_password(passNew)){
    alert('Mohon sesuaikan format password seperti sebelumnya!')
    passNewInput.val("");
    passNewInput.focus();
  }else if (hashOld !== password){
    alert('Password lama tidak sesuai! Mohon periksa kembali!')
    passOldInput.val("");
    passOldInput.focus();
  }else if(hashNew === hashOld){
    alert('Mohon masukkan password yang berbeda dengan password lama anda!')
    passNewInput.val("");
    passNewInput.focus();
  }else{
    $.ajax({
      type: "POST",
      url: "/reset_pass",
      data: {
        username_give: username,
        passnew_give: hashNew
      },
      success: function (response) {
        if(response['result'] ==='success'){
        alert("Password akun anda berhasil diupdate!");
        window.location.reload();
        }
      },
    });  
  }
  
}