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
                  if(post['confirm']===1){
                
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
                $('#listhome').append(temp_post);
                }
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
    } else if (timeD > 2) { 
      return "1 day ago";
    } else if (timeD < 7) {
      return parseInt(timeD) + " days ago";
    }
    return `${date.getFullYear()}.${date.getMonth() + 1}.${date.getDate()}`;
  }