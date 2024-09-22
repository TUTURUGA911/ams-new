function share (){
    let inputJudul = $('#judul');
    let inputLokasi = $('#lokasi');

    let judul = inputJudul.val();
    let lokasi = inputLokasi.val();
    let deskripsi = editor.getData();
    let file = $("#image")[0].files[0];

    console.log(file);

    if (judul === "") {
      alert("Mohon masukkan judul!")
      inputJudul.focus();
      return;
    } else if (lokasi === "") {
      alert("Mohon masukkan lokasi!")
      inputLokasi.focus();
      return;
    } else if (deskripsi === "") {
      alert("Mohon masukkan deskripsi!")
      editor.focus();
      return;
    } else if (!file) {
      alert("Mohon upload gambar!")
      return;
    } else {

      let today = new Date().toISOString()

      let form_data = new FormData();
      form_data.append("file_give", file);
      form_data.append("judul_give", judul);
      form_data.append("lokasi_give", lokasi);
      form_data.append("deskripsi_give", deskripsi);
      form_data.append("date_give", today);

      $.ajax({
          type: "POST",
          url: "/post_story",
          data: form_data,
          cache: false,
          contentType: false,
          processData: false,
          success: function (response) {
          if (response["result"] === "success") {
            alert(response["msg"]);
            window.location.reload();
          }
        },
      });
    }
};

function update (){
  let inputJudul = $('#judul');
  let inputLokasi = $('#lokasi');

  let judul = inputJudul.val();
  let lokasi = inputLokasi.val();
  let deskripsi = editor.getData();
  let postid = $('#postid').val();
  let file = $("#image")[0].files[0] || "";

  console.log(file);

  if (judul === "") {
    alert("Mohon masukkan judul!")
    inputJudul.focus();
    return;
  } else if (lokasi === "") {
    alert("Mohon masukkan lokasi!")
    inputLokasi.focus();
    return;
  } else if (deskripsi === "") {
    alert("Mohon masukkan deskripsi!")
    editor.focus();
    return;
  } else {

    let form_data = new FormData();
    form_data.append("id_give", postid);
    form_data.append("file_give", file);
    form_data.append("judul_give", judul);
    form_data.append("lokasi_give", lokasi);
    form_data.append("deskripsi_give", deskripsi);

    $.ajax({
        type: "POST",
        url: "/update_story",
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
        if (response["result"] === "success") {
          alert(response["msg"]);
          window.location.reload();
        }
      },
    });
  }
};

function delete_content(postid){
  if (confirm("Yakin ingin menghapus postingan ini?") == true) {
    $.ajax({
      type: "POST",
      url: "/delete/"+postid,
      data: {},
      cache: false,
      contentType: false,
      processData: false,
      success: function (response) {
      if (response["result"] === "success") {
        alert(response["msg"]);
        window.location.href = "/content";
      }
    },
  });
  }
}

function get_posts(){
    $.ajax({
        type: "GET",
        url: "/list_post",
        data: {},
        success: function (response) {
            console.log(response['posts']);
            if (response["result"] == "success") {
                let postlist = response['posts'];
                for(let i=0; i<postlist.length; i++){
                let post = postlist[i];
                let time_post = new Date(post["date"]);
                let time_before = time2str(time_post);
                console.log(time_before);
                let temp_post = `
                <div class="col-xl-4 col-md-6">
                <div class="post-item position-relative h-100">
                  <div class="post-img position-relative overflow-hidden">
                    <img src="static/${post['image']}" class="img-fluid list-img" alt="${post['judul']}">
                    <span class="post-date">${time_before}</span>
                  </div>
                  <div class="post-content d-flex flex-column">
                    <h3 class="post-title">${post['judul']}</h3>
                    <div class="meta d-flex align-items-center">
                      <div class="d-flex align-items-center">
                        <i class="bi bi-person"></i> <span class="ps-2">${post['username']}</span>
                      </div>
                    </div>
                    <div class="meta d-flex align-items-center">
                    <div class="d-flex align-items-center">
                    <i class="bi bi-geo-alt"></i> <span class="ps-2">${post['lokasi']}</span>
                  </div>
                  </div>
                    <div>${post['deskripsi'].slice(0, 150)} ...</div>
                    <hr>
                    <a href="/detail_content/${post['postid']}" class="readmore stretched-link"><span>Read More</span><i class="bi bi-arrow-right"></i></a>
                  </div>
                </div>
              </div>
                `
                $('#list').append(temp_post);
                
                }
            }
          }
    })
}

function time2str(date) {
  let today = new Date();
  let time = (today - date) / 1000 / 60; // minutes
  let timeH = time / 60;
  let timeD = timeH / 24;

  if (time < 5) {
    return "Just now";
  }
  if (time < 60) {
    return parseInt(time) + " minutes ago";
  } else if (timeH < 2) {
    return "1 hour ago";
  } else if (timeH < 24) {
    return parseInt(timeH) + " hours ago";
  } else if (timeD < 2) { 
    return "1 day ago";
  } else if (timeD < 7) {
    return parseInt(timeD) + " days ago";
  }
  return `${date.getFullYear()}.${date.getMonth() + 1}.${date.getDate()}`;
}

function num2str(count) {
  if (count > 10000) {
      return parseInt(count / 1000) + "k"
  }
  if (count > 500) {
      return parseInt(count / 100) / 10 + "k"
  }
  return count
}

function toggle_like(post_id, type) {
  console.log(post_id, type);
  let today = new Date().toISOString()
  let $a_like = $(`a[aria-label='heart']`);
  let $i_like = $a_like.find("i");
  if ($i_like.hasClass("bi-heart-fill")) {
    $.ajax({
      type: "POST",
      url: "/update_like",
      data: {
        post_id_give: post_id,
        type_give: type,
        date_give: today,
        action_give: "unlike",
      },
      success: function (response) {
        console.log("unlike");
        $i_like.addClass("bi-heart").removeClass("bi-heart-fill");
        console.log(num2str(response["count"]))
        $("span.like-num").text(num2str(response["count"]))
      },
    });
  } else {
    $.ajax({
      type: "POST",
      url: "/update_like",
      data: {
        post_id_give: post_id,
        type_give: type,
        date_give: today,
        action_give: "like",
      },
      success: function (response) {
        console.log("like");
        $i_like.addClass("bi-heart-fill").removeClass("bi-heart");
        $("span.like-num").text(response["count"]);
      },
    });
  }
}

function add_comment(post_id){
  let inputKomen = $('#comment-input');

  let komen = inputKomen.val();

  if (komen === "") {
    alert("Mohon isikan komentar!")
    inputKomen.focus();
    return;
  } else {
  let today = new Date().toISOString();
  $.ajax({
    type: "POST",
    url: "/add_comment",
    data: {
      post_id_give: post_id,
      comment_give: komen,
      date_give: today,
    },
    success: function (response) {
      if (response["result"] === "success") {
        alert(response["msg"]);
        window.location.reload();
      }
    },
  });
  }
}

function edit_comment(comment_id){
  let inputKomenEdit = $('#comment-edit');

  let komenEdit = inputKomenEdit.val();

  if (komenEdit === "") {
    alert("Mohon isikan komentar terbaru!")
    inputKomenEdit.focus();
    return;
  } else {
  $.ajax({
    type: "POST",
    url: "/update_comment",
    data: {
      comment_id_give: comment_id,
      comment_give: komenEdit,
    },
    success: function (response) {
      if (response["result"] === "success") {
        alert(response["msg"]);
        window.location.reload();
      }
    },
  });
  }
}

function delete_comment(commentid){
  if (confirm("Yakin ingin menghapus komentar ini?") == true) {
    $.ajax({
      type: "POST",
      url: "/deletecomment/"+commentid,
      data: {},
      cache: false,
      contentType: false,
      processData: false,
      success: function (response) {
      if (response["result"] === "success") {
        alert(response["msg"]);
        window.location.reload();
      }
    },
  });
  }
}

function search_post(){
    let searchPost = document
    .getElementById('search')
    .value.toLowerCase();
    
  let titleList = document.querySelectorAll('.post-title');
  console.log(titleList);
  for (let post of titleList) {
    if (post.innerText.toLowerCase().includes(searchPost)) {
      post.parentElement.parentElement.parentElement.style.display = 'block';
    } else {
      post.parentElement.parentElement.parentElement.style.display = 'none';
    }
  }
}
    
function auth_login_content(){
  $.ajax({
    type: "GET",
    url: "/auth_login",
    data: {},
    success: function (response) {
      if (response["result"] == "fail") {
        $('#btn-add').addClass('visually-hidden');
      }
      }
    })
}

function auth_login_detail(postcreator){
  $.ajax({
    type: "GET",
    url: "/auth_login/"+postcreator,
    data: {},
    success: function (response) {
      if (response["result"] == "fail") {
        $('#btn-post-control').addClass('visually-hidden');
      }
      }
    })
}

