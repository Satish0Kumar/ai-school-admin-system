$pages_dir = 'frontend\pages'
Get-ChildItem "$pages_dir\*.py" | ForEach-Object {
    $file = $_.FullName
    $content = Get-Content $file -Raw -Encoding UTF8
    $updated = $content -replace 'use_container_width=True', "width='stretch'"
    $updated = $updated -replace 'use_container_width=False', "width='content'"
    
    if ($updated -ne $content) {
        Set-Content $file $updated -Encoding UTF8
        Write-Host "Updated $($_.Name)"
    }
}
