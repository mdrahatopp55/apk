<?php
header("Content-Type: application/json; charset=UTF-8");
date_default_timezone_set('Asia/Dhaka');

function jsonResponse($data, $code = 200) {
    http_response_code($code);
    echo json_encode(
        $data,
        JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE
    );
    exit;
}

function randomIP() {
    return rand(1, 255) . "." . rand(0, 255) . "." . rand(0, 255) . "." . rand(1, 254);
}

function randomUserAgent() {
    $uas = [
        "Mozilla/5.0 (Linux; Android 10; SM-A107F) AppleWebKit/537.36 Chrome/124 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 Chrome/121 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2) AppleWebKit/605.1.15 Mobile/15E148",
        "Mozilla/5.0 (Linux; Android 12; Redmi Note 9) AppleWebKit/537.36 Chrome/132 Mobile Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/605.1.15 Version/16.4 Safari/605.1.15",
    ];
    return $uas[array_rand($uas)];
}

function randomReferer() {
    $refs = [
        "https://www.google.com/",
        "https://m.facebook.com/",
        "https://www.youtube.com/",
        "https://www.bing.com/",
        "https://www.instagram.com/"
    ];
    return $refs[array_rand($refs)];
}

// -------- INPUT --------
$username = isset($_GET['username']) ? trim($_GET['username']) : '';

if ($username === '') {
    jsonResponse([
        "status"  => false,
        "code"    => 400,
        "message" => "Parameter 'username' is required!"
    ], 400);
}

if (is_numeric($username)) {
    $username = "https://www.facebook.com/profile.php?id={$username}";
}

// -------- REQUEST BUILD --------
$api_url   = "https://www.fbprofileviewer.com/api/profile?username=" . urlencode($username);
$randomIP  = randomIP();
$randomUA  = randomUserAgent();
$randomRef = randomReferer();

$curl = curl_init();
curl_setopt_array($curl, [
    CURLOPT_URL => $api_url,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_TIMEOUT => 30,
    CURLOPT_HTTPHEADER => [
        "User-Agent: $randomUA",
        "X-Forwarded-For: $randomIP",
        "Client-IP: $randomIP",
        "Referer: $randomRef",
        "Accept: application/json",
        "Accept-Language: en-US,en;q=0.9"
    ]
]);

$response = curl_exec($curl);
$error    = curl_error($curl);
curl_close($curl);

// -------- ERROR: CURL --------
if ($error) {
    jsonResponse([
        "status"  => false,
        "code"    => 500,
        "message" => "cURL Error: $error"
    ], 500);
}

// -------- DECODE RESPONSE --------
$data = json_decode($response, true);

// If not valid JSON, just forward raw
if ($data === null) {
    jsonResponse([
        "status"             => true,
        "requested_username" => $username,
        "random_ip"          => $randomIP,
        "random_user_agent"  => $randomUA,
        "random_referer"     => $randomRef,
        "raw_response"       => $response
    ]);
}

// -------- HANDLE RATE LIMIT (YOUR ERROR) --------
if (isset($data['success']) && $data['success'] === false && isset($data['error'])) {

    // If they say "Too many requests..." → return 429
    if (stripos($data['error'], 'Too many requests') !== false) {
        jsonResponse([
            "status"             => false,
            "code"               => 429,
            "message"            => $data['error'],
            "retry_after"        => isset($data['retryAfter']) ? $data['retryAfter'] : "unknown",
            "patreon_link"       => isset($data['patreonLink']) ? $data['patreonLink'] : null,
            "requested_username" => $username
        ], 429);
    }

    // Other errors from their API
    jsonResponse([
        "status"             => false,
        "code"               => 502,
        "message"            => $data['error'],
        "requested_username" => $username
    ], 502);
}

// -------- SUCCESS --------
jsonResponse([
    "status"             => true,
    "requested_username" => $username,
    "random_ip"          => $randomIP,
    "random_user_agent"  => $randomUA,
    "random_referer"     => $randomRef,
    "data"               => $data
]);