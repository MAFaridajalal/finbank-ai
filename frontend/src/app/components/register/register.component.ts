import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSelectModule,
    MatSnackBarModule
  ],
  template: `
    <div class="register-container">
      <mat-card class="register-card">
        <mat-card-header>
          <mat-card-title>Register New Customer</mat-card-title>
          <mat-card-subtitle>Add a new customer to the banking system</mat-card-subtitle>
        </mat-card-header>

        <mat-card-content>
          <form [formGroup]="registerForm" (ngSubmit)="onSubmit()">
            <div class="form-row">
              <mat-form-field appearance="outline" class="half-width">
                <mat-label>First Name</mat-label>
                <input matInput formControlName="firstName" required>
                @if (registerForm.get('firstName')?.hasError('required') && registerForm.get('firstName')?.touched) {
                  <mat-error>First name is required</mat-error>
                }
              </mat-form-field>

              <mat-form-field appearance="outline" class="half-width">
                <mat-label>Last Name</mat-label>
                <input matInput formControlName="lastName" required>
                @if (registerForm.get('lastName')?.hasError('required') && registerForm.get('lastName')?.touched) {
                  <mat-error>Last name is required</mat-error>
                }
              </mat-form-field>
            </div>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Email</mat-label>
              <input matInput type="email" formControlName="email" required>
              @if (registerForm.get('email')?.hasError('required') && registerForm.get('email')?.touched) {
                <mat-error>Email is required</mat-error>
              }
              @if (registerForm.get('email')?.hasError('email')) {
                <mat-error>Please enter a valid email</mat-error>
              }
              @if (registerForm.get('email')?.hasError('serverError')) {
                <mat-error>{{ registerForm.get('email')?.getError('serverError') }}</mat-error>
              }
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Phone</mat-label>
              <input matInput formControlName="phone">
              @if (registerForm.get('phone')?.hasError('serverError')) {
                <mat-error>{{ registerForm.get('phone')?.getError('serverError') }}</mat-error>
              }
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Address</mat-label>
              <input matInput formControlName="address">
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>City</mat-label>
              <input matInput formControlName="city">
            </mat-form-field>

            <div class="form-row">
              <mat-form-field appearance="outline" class="half-width">
                <mat-label>Customer Tier</mat-label>
                <mat-select formControlName="tier">
                  <mat-option value="Basic">Basic</mat-option>
                  <mat-option value="Premium">Premium</mat-option>
                  <mat-option value="VIP">VIP</mat-option>
                </mat-select>
              </mat-form-field>

              <mat-form-field appearance="outline" class="half-width">
                <mat-label>Branch</mat-label>
                <mat-select formControlName="branch">
                  <mat-option value="Downtown">Downtown</mat-option>
                  <mat-option value="Westside">Westside</mat-option>
                  <mat-option value="Airport">Airport</mat-option>
                  <mat-option value="Bellevue">Bellevue</mat-option>
                </mat-select>
              </mat-form-field>
            </div>

            <div class="button-row">
              <button mat-raised-button type="button" (click)="onCancel()">Cancel</button>
              <button mat-raised-button color="primary" type="submit" [disabled]="!registerForm.valid || submitting">
                {{ submitting ? 'Creating...' : 'Create Customer' }}
              </button>
            </div>
          </form>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .register-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100%;
      padding: 24px;
    }

    .register-card {
      max-width: 600px;
      width: 100%;
    }

    mat-card-header {
      margin-bottom: 24px;
    }

    form {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .form-row {
      display: flex;
      gap: 16px;
    }

    .full-width {
      width: 100%;
    }

    .half-width {
      flex: 1;
    }

    .button-row {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      margin-top: 16px;
    }
  `]
})
export class RegisterComponent {
  registerForm: FormGroup;
  submitting = false;

  constructor(
    private fb: FormBuilder,
    private apiService: ApiService,
    private router: Router,
    private snackBar: MatSnackBar
  ) {
    this.registerForm = this.fb.group({
      firstName: ['', Validators.required],
      lastName: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      phone: [''],
      address: [''],
      city: [''],
      tier: ['Basic'],
      branch: ['Downtown']
    });
  }

  onSubmit(): void {
    if (this.registerForm.valid) {
      this.submitting = true;
      const formData = this.registerForm.value;

      // Create customer via direct API (not chat)
      const customerData = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        phone: formData.phone || '',
        address: formData.address || '',
        city: formData.city || '',
        tier: formData.tier || 'Basic',
        branch: formData.branch || 'Downtown'
      };

      this.apiService.createCustomer(customerData).subscribe({
        next: (response) => {
          this.submitting = false;

          if (response.success) {
            // Success - show success notification and redirect
            this.snackBar.open(
              `✅ Customer created successfully! ID: ${response.customer_id}`,
              'Close',
              {
                duration: 3000,
                panelClass: ['success-snackbar']
              }
            );
            // Redirect to data browser
            setTimeout(() => {
              this.router.navigate(['/data']);
            }, 500);
          } else {
            // Validation errors - display them
            if (response.errors) {
              const errorMessages = Object.entries(response.errors)
                .map(([field, message]) => `• ${field}: ${message}`)
                .join('\n');

              this.snackBar.open(
                `❌ Validation failed:\n${errorMessages}`,
                'Close',
                {
                  duration: 10000,
                  panelClass: ['error-snackbar']
                }
              );

              // Set form errors to show under fields
              Object.entries(response.errors).forEach(([field, message]) => {
                const controlName = this.getControlName(field);
                if (controlName && this.registerForm.get(controlName)) {
                  this.registerForm.get(controlName)?.setErrors({ serverError: message });
                }
              });
            } else {
              this.snackBar.open(
                `❌ ${response.message}`,
                'Close',
                {
                  duration: 5000,
                  panelClass: ['error-snackbar']
                }
              );
            }
          }
        },
        error: (error) => {
          this.submitting = false;
          this.snackBar.open(
            `❌ Error creating customer: ${error.message || 'Unknown error'}`,
            'Close',
            {
              duration: 5000,
              panelClass: ['error-snackbar']
            }
          );
        }
      });
    }
  }

  private getControlName(field: string): string | null {
    const fieldMap: { [key: string]: string } = {
      'email': 'email',
      'phone': 'phone',
      'tier': 'tier',
      'branch': 'branch'
    };
    return fieldMap[field] || null;
  }

  onCancel(): void {
    this.router.navigate(['/data']);
  }
}
