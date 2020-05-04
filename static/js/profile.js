async function addFriend() {
    let friendButton = document.getElementById("friend_button");
    let email = document.getElementById("email").innerText;

    if (friendButton.innerText === "Friend") {
        friendButton.innerText = "Unfriend";
    } else friendButton.innerText = "Friend";

    let data = { email };

    await fetch("/toggleFriend", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });
}
