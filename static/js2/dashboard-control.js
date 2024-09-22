function openuser() {
  $("#kelolauser").removeClass("visually-hidden");
  $("#kelolapost").addClass("visually-hidden");
  $("#kelolapesan").addClass("visually-hidden");
  $("#btn-user").addClass("active");
  $("#btn-post").removeClass("active");
  $("#btn-pesan").removeClass("active");
}

function openpost() {
  $("#kelolapost").removeClass("visually-hidden");
  $("#kelolauser").addClass("visually-hidden");
  $("#kelolapesan").addClass("visually-hidden");
  $("#btn-post").addClass("active");
  $("#btn-user").removeClass("active");
  $("#btn-pesan").removeClass("active");
}

function openpesan() {
  $("#kelolapost").addClass("visually-hidden");
  $("#kelolauser").addClass("visually-hidden");
  $("#kelolapesan").removeClass("visually-hidden");
  $("#btn-post").removeClass("active");
  $("#btn-user").removeClass("active");
  $("#btn-pesan").addClass("active");
}

function openunc() {
  $("#unconfirm").removeClass("visually-hidden");
  $("#accpost").addClass("visually-hidden");
  $("#decpost").addClass("visually-hidden");
  $("#btn-unc").addClass("active");
  $("#btn-acc").removeClass("active");
  $("#btn-dec").removeClass("active");
}

function openacc() {
  $("#unconfirm").addClass("visually-hidden");
  $("#accpost").removeClass("visually-hidden");
  $("#decpost").addClass("visually-hidden");
  $("#btn-unc").removeClass("active");
  $("#btn-acc").addClass("active");
  $("#btn-dec").removeClass("active");
}

function opendec() {
  $("#unconfirm").addClass("visually-hidden");
  $("#accpost").addClass("visually-hidden");
  $("#decpost").removeClass("visually-hidden");
  $("#btn-unc").removeClass("active");
  $("#btn-acc").removeClass("active");
  $("#btn-dec").addClass("active");
}

function showPost() {
  if ($("select").val() === "unconfirm") {
    $("#unconfirm").removeClass("visually-hidden");
    $("#accpost").addClass("visually-hidden");
    $("#decpost").addClass("visually-hidden");
    $("#btn-unc").addClass("active");
    $("#btn-acc").removeClass("active");
    $("#btn-dec").removeClass("active");
  } else if ($("select").val() === "acc") {
    $("#unconfirm").addClass("visually-hidden");
    $("#accpost").removeClass("visually-hidden");
    $("#decpost").addClass("visually-hidden");
    $("#btn-unc").removeClass("active");
    $("#btn-acc").addClass("active");
    $("#btn-dec").removeClass("active");
  } else if ($("select").val() === "dec") {
    $("#unconfirm").addClass("visually-hidden");
    $("#accpost").addClass("visually-hidden");
    $("#decpost").removeClass("visually-hidden");
    $("#btn-unc").removeClass("active");
    $("#btn-acc").removeClass("active");
    $("#btn-dec").addClass("active");
  }
}

function get_postlist() {
    $("#postlist").empty();
    $.ajax({
      type: "GET",
      url: "/list_postadmin",
      data: {},
      success: function (response) {
        if (response["result"] == "success") {
          let postlist = response["posts"];
          $('#countunc').text(response['count']['unc'] + ' Postingan');
          $('#countacc').text(response['count']['acc'] + ' Postingan');
          $('#countdec').text(response['count']['dec'] + ' Postingan');

          if(response['count']['unc'] === 0){
            let temp_post=`
            <div class="col-xl-4 col-md-6">
            <h5>Tidak ada postingan masuk</h5>
            </div>`;
            $("#listunconfirm").append(temp_post);
          }else if(response['count']['acc'] === 0){
            let temp_post=`
            <div class="col-xl-4 col-md-6">
            <h5>Tidak ada postingan diterima</h5>
            </div>`;
            $("#listacc").append(temp_post);
          }else if(response['count']['dec'] === 0){
            let temp_post=`
            <div class="col-xl-4 col-md-6">
            <h5>Tidak ada postingan ditolak/telah dihapus</h5>
            </div>`;
            $("#listdec").append(temp_post);
          }
          for (let i = 0; i < postlist.length; i++) {
            let post = postlist[i];
            if (post["confirm"] === 0) {
            let temp_post = `
            <div class="col-xl-4 col-md-6">
            <div class="post-item position-relative h-100">
              <div class="post-img position-relative overflow-hidden">
                <img src="static/${post['image']}" class="img-fluid list-img" alt="${post['judul']}">
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
                <div>
                <button type="button" class="btn btn-primary" onclick="terimapost('${post["postid"]}')">Terima</button>
              <button type="button" class="btn btn-danger" data-bs-toggle="modal"
              data-bs-target="#modal${post['postid']}">Tolak</button></td>
              </div>
              <hr/>
              <a href="/detail_content/${post['postid']}" class="readmore"><span>Read More</span><i class="bi bi-arrow-right"></i></a>
              </div>
            </div>
            <div
            class="modal fade"
            id="modal${post['postid']}"
            tabindex="-1"
            role="dialog"
            aria-labelledby="shareExperienceModal"
            aria-hidden="true"
          >
            <div class="modal-dialog" role="document">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title" id="blockModalLabel">Tolak Postingan "${post["judul"]}"</h5>
                  <button
                    type="button"
                    class="btn-close"
                    data-bs-dismiss="modal"
                    aria-label="Close"
                  ></button>
                </div>
                <div class="modal-body">
                  <label for="reason">Alasan Penolakan:</label>
                  <textarea
                    class="form-control"
                    id="reason${post["postid"]}"
                    row="2"
                    placeholder="Masukkan alasan penolakan"
                  ></textarea>
                </div>
                <div class="modal-footer">
                  <button
                    type="button"
                    class="btn btn-secondary"
                    data-bs-dismiss="modal"
                  >
                    Cancel
                  </button>
                  <button type="button" onclick="tolakpost('${post['postid']}')" class="btn btn-primary">Tolak</button>
                </div>
              </div>
            </div>
          </div>
          </div>
            `;
            $("#listunconfirm").append(temp_post);
          }else if (post["confirm"] === 1) {
            let temp_post = `
            <div class="col-xl-4 col-md-6">
            <div class="post-item position-relative h-100">
              <div class="post-img position-relative overflow-hidden">
                <img src="static/${post['image']}" class="img-fluid list-img" alt="${post['judul']}">
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
                <a href="/detail_content/${post['postid']}" class="readmore"><span>Read More</span><i class="bi bi-arrow-right"></i></a>
                <hr>
                <div>
                <button type="button" class="btn btn-danger" onclick="hapuspost('${post["postid"]}')">Hapus</button>
              </div>
              </div>
            </div>
          </div>
            `;
            $("#listacc").append(temp_post);
          }else if (post["confirm"] === 2) {
            let temp_post = `
            <div class="col-xl-4 col-md-6">
            <div class="post-item position-relative h-100">
              <div class="post-img position-relative overflow-hidden">
                <img src="static/${post['image']}" class="img-fluid list-img" alt="${post['judul']}">
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
                <div>
                <button type="button" class="btn btn-danger" onclick="hapuspost('${post["postid"]}')">Hapus</button>
              </div>
            </div>
          </div>
            `;
            $("#listdec").append(temp_post);
          }
        }
        }
      },
    });
  }

  function terimapost(postid) {
    let type = 1;
    let today = new Date().toISOString()
    console.log(postid, type);

    $.ajax({
      type: "POST",
      url: "/confirm_post",
      data: {
        id_give: postid,
        type_give: type,
        date_give: today,
      },
      success: function (response) {
        if (response["result"] === "success") {
          window.location.reload();
        }
      },
    });
  }

  function tolakpost(postid) {
    let type = 2;
    let today = new Date().toISOString()
    let reason = $('#reason'+postid).val()
    console.log(postid, type, reason);

    $.ajax({
      type: "POST",
      url: "/confirm_post",
      data: {
        id_give: postid,
        type_give: type,
        reason_give: reason,
        date_give: today,
      },
      success: function (response) {
        if (response["result"] === "success") {
          window.location.reload();
        }
      },
    });
  }

  function hapuspost(postid) {
  
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
        window.location.reload();
      }
    },
  });
  }
  }

  function get_user() {
    $("#userlist").empty();
    $.ajax({
      type: "GET",
      url: "/manageuser",
      data: {},
      success: function (response) {
        if (response["result"] == "success") {
            let userlist = response['data'];
            console.log(userlist);
            for (let i = 0; i < userlist.length; i++) {
              let user = userlist[i];
              let status = '';
              let btn_block = '';
              if (user['blocked']=== true){
                status='Diblokir';
                btn_block=`
                <button type="button" class="btn btn-primary" onclick="unblockuser('${user["username"]}')">Buka Blokir</button>
                `;
              }else{
                status='Aktif';
                btn_block=`
                <button type="button" class="btn btn-danger" 
                data-bs-toggle="modal"
                data-bs-target="#modal${user['_id']}"
                >Blokir</button>
                
                `;
              }
              let temp_post = `
              <tr>
              <td>${user["profile_name"]}</td>
              <td>${status}</td>
              <td>${user["count_post"]}</td>
              <td>
              ${btn_block}
              <div
              class="modal fade"
              id="modal${user['_id']}"
              tabindex="-1"
              role="dialog"
              aria-labelledby="shareExperienceModal"
              aria-hidden="true"
            >
              <div class="modal-dialog" role="document">
                <div class="modal-content">
                  <div class="modal-header">
                    <h5 class="modal-title" id="blockModalLabel">Blokir User "${user["profile_name"]}"</h5>
                    <button
                      type="button"
                      class="btn-close"
                      data-bs-dismiss="modal"
                      aria-label="Close"
                    ></button>
                  </div>
                  <div class="modal-body">
                    <label for="reason">Alasan Pemblokiran:</label>
                    <textarea
                      class="form-control"
                      id="reason${user["username"]}"
                      row="2"
                      placeholder="Masukkan alasan pemblokiran"
                    ></textarea>
                  </div>
                  <div class="modal-footer">
                    <button
                      type="button"
                      class="btn btn-secondary"
                      data-bs-dismiss="modal"
                    >
                      Cancel
                    </button>
                    <button type="button" class="btn btn-primary" onclick="blockuser('${user["username"]}')">Blokir</button>
                  </div>
                </div>
              </div>
            </div>
              </td>
              </tr>
              `;
              $("#userlist").append(temp_post);

            }
            $("#tableuser").DataTable();
          }
      }
    })
}

function get_pesan() {
    $("#pesanlist").empty();
    $.ajax({
      type: "GET",
      url: "/get_pesan",
      data: {},
      success: function (response) {
        if (response["result"] == "success") {
            let pesanlist = response['data'];
            console.log(pesanlist);
            if (pesanlist.length>0){
            for (let i = 0; i <pesanlist.length; i++) {
              
              let pesan=pesanlist[i];
              let status = '';
              if (pesan['show'] === false){
                status = `
                <td>Belum dikonfirmasi</td>
                <td>
                <button type="button" class="btn btn-primary" onclick="showmsg('${pesan["_id"]}')">Tampilkan</button>
              <button type="button" class="btn btn-danger" onclick="deletemsg('${pesan["_id"]}')">Hapus</button></td>
                `
              }else{
                status = `
                <td>Ditampilkan</td>
                <td>
              <button type="button" class="btn btn-danger" onclick="deletemsg('${pesan["_id"]}')">Hapus</button></td>
                `;
              }
              let temp_post = `
              <tr>
              <td>${pesan["username"]}</td>
              <td>${pesan["message"]}</td>
              ${status}
              </tr>
              `;
              $("#pesanlist").append(temp_post);

            }            
          }else{
              let temp_post = `
              <tr><td colspan="4">Tidak ada pesan masuk</td></tr>
              `
              $("#pesanlist").append(temp_post);
            }
          }
          $("#tablepesan").DataTable();
      }
    })
}

function showmsg(idmsg){
    $.ajax({
      type: "POST",
      url: "/confirm_msg",
      data: {
        id_give: idmsg,
        type_give: 'show',
      },
      success: function (response) {
        if (response["result"] === "success") {
          get_pesan();
        }
      },
    });
}
function deletemsg(idmsg){
    $.ajax({
      type: "POST",
      url: "/confirm_msg",
      data: {
        id_give: idmsg,
        type_give: 'delete',
      },
      success: function (response) {
        if (response["result"] === "success") {
          get_pesan();
        }
      },
    });
}

function blockuser(username){
    let today = new Date().toISOString()
    let reason = $('#reason'+username).val()

    $.ajax({
      type: "POST",
      url: "/blockuser",
      data: {
        username_give: username,
        reason_give: reason,
        date_give: today,
      },
      success: function (response) {
        if (response["result"] === "success") {
          window.location.reload();
        }
      },
    });
}

function unblockuser(username){
    $.ajax({
      type: "POST",
      url: "/unblockuser",
      data: {
        username_give: username,
      },
      success: function (response) {
        if (response["result"] === "success") {
          window.location.reload();
        }
      },
    });
}