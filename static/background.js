var email = undefined;

chrome.identity.getProfileUserInfo(function(info) {
    email = info.email;
});

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse){
    sendResponse({'email': email});
});

chrome.runtime.onInstalled.addListener((details) => {
    chrome.tabs.create({ // Makeshift workaround to get the extension to use the microphone
        url: chrome.runtime.getURL('../templates/gum.html'),
        active: true
    });
    /*
    A methodology can be employed to check if any mic recording extension allows
    inline Javascript so we can read how they allowed microphone access without
    opening a faux tab which asks for the permission on the extension's behalf.
    */
})