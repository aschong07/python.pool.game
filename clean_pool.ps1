# Clean pool.py by removing duplicate code
$filePath = "c:\Users\alexi\Desktop\Python Pool Game\python.pool.game\pool.py"
$content = Get-Content $filePath

# Find the first occurrence of "if __name__ == "__main__":"
$mainLineIndex = -1
for ($i = 0; $i -lt $content.Length; $i++) {
    if ($content[$i] -match '^if __name__ == "__main__":') {
        $mainLineIndex = $i
        break
    }
}

if ($mainLineIndex -ge 0) {
    # Keep everything up to and including "main()" which should be 1 line after
    $cleanContent = $content[0..($mainLineIndex + 1)]
    $cleanContent | Set-Content $filePath -Force
    Write-Host "File cleaned. Kept $($mainLineIndex + 2) lines."
} else {
    Write-Host "Could not find main block!"
}
