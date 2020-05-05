async function addFriend(friendButton) {
    let email = friendButton.dataset.email;

    if (friendButton.innerText === "Add Friend") {
        friendButton.innerText = "Remove Friend";
        friendButton.classList.remove("add_friend");
        friendButton.classList.add("remove_friend");
    } else {
        friendButton.innerText = "Add Friend";
        friendButton.classList.remove("remove_friend");
        friendButton.classList.add("add_friend");
    }

    let data = { email };

    await fetch("/toggleFriend", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });
}
