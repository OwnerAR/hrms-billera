# Fix untuk Error: Duplicate Account Number di Chart of Accounts Indonesia

## Deskripsi Masalah

Error yang terjadi saat setup wizard:
```
frappe.exceptions.ValidationError: Account Number 1150.000 already used in account 1150.000 - Biaya di Bayar di Muka - AMI
```

Masalah ini terjadi karena ada duplikasi account number dalam template Chart of Accounts untuk Indonesia di ERPNext.

## Solusi yang Diimplementasikan

Saya telah membuat 3 fix untuk mengatasi masalah ini:

### 1. **Override Account Doctype** (`hrms/overrides/account.py`)
   - Override method `validate_account_number()` di Account doctype
   - Ketika menemukan duplikasi account number, sistem akan:
     - Menghapus account number yang duplikat (bukan error)
     - Membuat log warning
     - Menampilkan notifikasi ke user
   - Fix ini mencegah error saat pembuatan account

### 2. **Update Company Override** (`hrms/overrides/company.py`)
   - Menambahkan function `fix_duplicate_account_numbers()` 
   - Akan otomatis membersihkan duplikasi account number saat validasi company
   - Berjalan setelah company dibuat

### 3. **Patch Post-Install** (`hrms/patches/post_install/fix_duplicate_account_numbers.py`)
   - Patch yang akan berjalan setelah instalasi
   - Membersihkan semua duplikasi account number yang sudah ada
   - Mencari dan memperbaiki untuk semua company

## Cara Mengaplikasikan Fix

### Untuk Fresh Installation (Docker)

1. **Build ulang container dengan source code yang sudah diperbaiki:**
   ```bash
   # Matikan container yang sedang berjalan
   docker-compose down -v
   
   # Build dan jalankan ulang
   docker-compose up --build
   ```

2. **Tunggu proses setup selesai**, fix akan otomatis berjalan

### Untuk Installation yang Sudah Ada

Jika database sudah dibuat dan terjadi error:

1. **SSH/Akses ke container atau VPS:**
   ```bash
   # Jika menggunakan docker
   docker exec -it <container_name> bash
   
   # Navigate ke bench directory
   cd /home/frappe/frappe-bench
   ```

2. **Jalankan patch manual:**
   ```bash
   # Reload HRMS app untuk load override baru
   bench --site <site_name> reload-doctype
   
   # Atau migrate untuk jalankan semua patches
   bench --site <site_name> migrate
   ```

3. **Atau jalankan script Python manual:**
   ```bash
   bench --site <site_name> console
   ```
   
   Kemudian di console Python:
   ```python
   from hrms.patches.post_install.fix_duplicate_account_numbers import execute
   execute()
   ```

4. **Clear cache:**
   ```bash
   bench --site <site_name> clear-cache
   bench restart
   ```

## File yang Diubah

1. ✅ `hrms/overrides/account.py` (NEW) - Override Account doctype
2. ✅ `hrms/overrides/company.py` (MODIFIED) - Tambah function fix duplicate
3. ✅ `hrms/hooks.py` (MODIFIED) - Register override Account
4. ✅ `hrms/patches/post_install/fix_duplicate_account_numbers.py` (NEW) - Patch file
5. ✅ `hrms/patches.txt` (MODIFIED) - Register patch

## Verifikasi

Setelah fix diaplikasikan, Anda bisa verifikasi dengan:

```bash
# Check di bench console
bench --site <site_name> console
```

```python
import frappe

# Check duplicate account numbers
duplicates = frappe.db.sql("""
    SELECT company, account_number, COUNT(*) as count
    FROM `tabAccount`
    WHERE account_number IS NOT NULL AND account_number != ''
    GROUP BY company, account_number
    HAVING count > 1
""", as_dict=True)

print(f"Found {len(duplicates)} duplicate account numbers")
print(duplicates)
```

Jika tidak ada duplikasi, hasilnya akan `[]` (empty list).

## Catatan

- Fix ini tidak akan menghapus atau mengubah struktur Chart of Accounts
- Hanya account number yang duplikat yang akan di-clear
- Account pertama yang dibuat akan tetap memiliki account number
- Account kedua dst yang duplikat akan di-clear account numbernya
- Fungsi accounting tetap normal karena account number bersifat opsional

## Support

Jika masih mengalami masalah:
1. Check log: `bench --site <site_name> console` dan lihat frappe.log
2. Restart bench: `bench restart`
3. Clear cache: `bench clear-cache`

---

**Dibuat**: 25 Oktober 2025  
**Untuk**: HRMS Billera Project  
**Fix untuk**: Duplicate Account Number di Indonesia Chart of Accounts

