function readnotif(notifid){
    $.ajax({
        type: "POST",
        url: "/read_notif",
        data: {
          id_give: notifid
        },
        success: function (response) {
          if (response["result"] === "success") {
            window.location.reload();
          }
        },
      });
}

function getnotif() {
    $.ajax({
      type: "GET",
      url: "/getnotif",
      data: {},
      success: function (response) {
        if (response["result"] === "success") {
          for (let i = 0; i < response["notif"].length; i++) {
            let data = response["notif"][i];
            let classlist = "";
            if (data.read === false) {
              classlist = "unread";
            }
            let type_notif = "";
            if (data.type === "post") {
              type_notif = "Permintaan Postingan";
            } else if (data.type === "like"){
                type_notif = "Tanggapan Postingan";
            } else if (data.type === "comment"){
                type_notif = "Komentar Postingan";
            }
            let btn_read = "";
            if (data.read === false) {
              btn_read = `
              |
                      <a
                        class=""
                        onclick="readnotif('${data._id}')"
                        style="cursor: pointer"
                        >Tandai telah dibaca</a
                      >
              `;
            }
            let temp_notif = `
          <div
              class="notification-list ${classlist}"
            >
              <div class="notification-list_content">
                <div class="notification-list_img">
                  <img
                    src="./static/${data.user_from.profile_pic_real}"
                    alt="user"
                  />
                </div>
                <div class="notification-list_detail">
                  <p>
                    ${type_notif} | Dari <a href="/user/${data.from}"><b>${data.from}</b></a>
                  </p>
                  <p class="text-muted">${data.isi}</p>
                  <p class="text-muted">
                    <small
                      >${data.timenotif} -
                      <a href="/detail_content/${data.toid}"
                        >Review postingan</a
                      >
                      ${btn_read}
                    </small>
                  </p>
                </div>
              </div>
            </div>
          `;
            $("#listnotif").append(temp_notif);
          }
        }
      },
    });
  }