function login_auth (){
  $.ajax({
    type: "GET",
    url: "/auth_login",
    data: {},
    success: function (response) {
      if (response["result"] == "success") {
        if(response.data.level == "1"){
          let temp_navbar = `
          <ul>
            <li><a href="/" id="navhome">Home</a></li>
            <li><a href="/shop" id="navcontent">Shop</a></li>
            <li><a href="/contact" id="navmedia">Contact</a></li>
            <li><a href="/about" id="navabout">About Us</a></li>
            <li><a class="" onclick="sign_out()" style="cursor: pointer" id="navlogout">Logout</a></li>
          </ul>
  `;
  $('#navbar').append(temp_navbar);

        }else if(response.data.level == "2"){
        console.log(response.data);
        let unread = '';
        if (response.notif > 0){
          unread = `&nbsp;<i class="bi bi-circle-fill text-danger"></i>`
        }
        let temp_navbar = `
        <ul>
          <li><a href="/" id="navhome">Home</a></li>
          <li><a href="/shop" id="navcontent">Shop</a></li>
          <li><a href="/contact" id="navmedia">Contact</a></li>
          <li><a href="/about" id="navabout">About Us</a></li>
          <li class="nav-item ">
                        <a class="nav-link" href="/cart">
                            <i class="bi bi-cart-fill" style="font-size: 1.2rem;"></i>
                        </a>
                    </li>
                    <li class="nav-item active">
                        <a class="nav-link" href="/orders">Orders</a>
                    </li>
          <li><a href="/user/${response.data.username}" id="navmedia">Profil</a></li>
          <li><a class="" onclick="sign_out()" style="cursor: pointer" id="navlogout">
Logout&nbsp;&nbsp;<img
class="rounded-circle shadow-1-strong me-3"
src="/static/${response.data.profile_icon}"
alt="avatar"
width="30"
height="30"
/></a></li>
        </ul>
`;
$('#navbar').append(temp_navbar);
        }

      } else {
        let temp_navbar = `
          <ul>
            <li><a href="/" id="navhome">Home</a></li>
            <li><a href="/shop" id="navcontent">Shop</a></li>
            <li><a href="/contact" id="navmedia">Contact</a></li>
            <li><a href="/about" id="navabout">About Us</a></li>
            <li><a href="/login" id="navlogin">Login</a></li>
          </ul>
  `;
  
  $('#navbar').append(temp_navbar);
      }
    },
  });
}

login_auth();

function sign_out() {
  Swal.fire({
    title: "Are you sure?",
    text: "Anda akan logout dari akun anda",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#3085d6",
    cancelButtonColor: "#d33",
    confirmButtonText: "Ya, logout!"
  }).then((result) => {
    if (result.isConfirmed) {
      $.removeCookie("mytoken", { path: "/" });
      Swal.fire({
          title: "Ter-logout!",
          text: "Anda sudah logout dari akun anda!",
          icon: "warning"
      }).then((result) => {
  /* Read more about isConfirmed, isDenied below */
            if (result.isConfirmed) {
              window.location.href = "/login";
              }
      })
      
    }
  });

}

