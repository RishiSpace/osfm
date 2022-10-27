#pragma once
#include<iostream>

namespace osfmgf {

	using namespace System;
	using namespace System::ComponentModel;
	using namespace System::Collections;
	using namespace System::Windows::Forms;
	using namespace System::Data;
	using namespace System::Drawing;

	/// <summary>
	/// Summary for Main
	/// </summary>
	public ref class Install : public System::Windows::Forms::Form
	{
	public:
		Install(void)
		{
			InitializeComponent();
			//
			//TODO: Add the constructor code here
			//
		}

	protected:
		/// <summary>
		/// Clean up any resources being used.
		/// </summary>
		~Install()
		{
			if (components)
			{
				delete components;
			}
		}
	private: System::Windows::Forms::Panel^ panel1;
	private: System::Windows::Forms::PictureBox^ pictureBox1;

	private: System::Windows::Forms::Button^ button2;
	private: System::Windows::Forms::Button^ button4;
	private: System::Windows::Forms::Button^ button3;
	private: System::Windows::Forms::Button^ button1;
	private: System::Windows::Forms::Panel^ panel2;
	private: System::Windows::Forms::Button^ button5;
	private: System::Windows::Forms::Label^ label1;
	private: System::Windows::Forms::Button^ button6;
	private: System::Windows::Forms::Button^ button7;
	private: System::Windows::Forms::Label^ label2;
	private: System::Windows::Forms::Button^ button13;
	private: System::Windows::Forms::Button^ button12;
	private: System::Windows::Forms::Button^ button11;
	private: System::Windows::Forms::Button^ button10;
	private: System::Windows::Forms::Button^ button9;
	private: System::Windows::Forms::Button^ button8;


	protected:

	private:
		/// <summary>
		/// Required designer variable.
		/// </summary>
		System::ComponentModel::Container ^components;

#pragma region Windows Form Designer generated code
		/// <summary>
		/// Required method for Designer support - do not modify
		/// the contents of this method with the code editor.
		/// </summary>
		void InitializeComponent(void)
		{
			System::ComponentModel::ComponentResourceManager^ resources = (gcnew System::ComponentModel::ComponentResourceManager(Install::typeid));
			this->panel1 = (gcnew System::Windows::Forms::Panel());
			this->label2 = (gcnew System::Windows::Forms::Label());
			this->button13 = (gcnew System::Windows::Forms::Button());
			this->button12 = (gcnew System::Windows::Forms::Button());
			this->button11 = (gcnew System::Windows::Forms::Button());
			this->button10 = (gcnew System::Windows::Forms::Button());
			this->button9 = (gcnew System::Windows::Forms::Button());
			this->button8 = (gcnew System::Windows::Forms::Button());
			this->button7 = (gcnew System::Windows::Forms::Button());
			this->button6 = (gcnew System::Windows::Forms::Button());
			this->button5 = (gcnew System::Windows::Forms::Button());
			this->panel2 = (gcnew System::Windows::Forms::Panel());
			this->label1 = (gcnew System::Windows::Forms::Label());
			this->button4 = (gcnew System::Windows::Forms::Button());
			this->button3 = (gcnew System::Windows::Forms::Button());
			this->button1 = (gcnew System::Windows::Forms::Button());
			this->button2 = (gcnew System::Windows::Forms::Button());
			this->pictureBox1 = (gcnew System::Windows::Forms::PictureBox());
			this->panel1->SuspendLayout();
			this->panel2->SuspendLayout();
			(cli::safe_cast<System::ComponentModel::ISupportInitialize^>(this->pictureBox1))->BeginInit();
			this->SuspendLayout();
			// 
			// panel1
			// 
			this->panel1->AutoSizeMode = System::Windows::Forms::AutoSizeMode::GrowAndShrink;
			this->panel1->BackColor = System::Drawing::SystemColors::ActiveCaptionText;
			this->panel1->Controls->Add(this->label2);
			this->panel1->Controls->Add(this->button13);
			this->panel1->Controls->Add(this->button12);
			this->panel1->Controls->Add(this->button11);
			this->panel1->Controls->Add(this->button10);
			this->panel1->Controls->Add(this->button9);
			this->panel1->Controls->Add(this->button8);
			this->panel1->Controls->Add(this->button7);
			this->panel1->Controls->Add(this->button6);
			this->panel1->Controls->Add(this->button5);
			this->panel1->Controls->Add(this->panel2);
			this->panel1->Controls->Add(this->button4);
			this->panel1->Controls->Add(this->button3);
			this->panel1->Controls->Add(this->button1);
			this->panel1->Controls->Add(this->button2);
			this->panel1->Controls->Add(this->pictureBox1);
			this->panel1->Location = System::Drawing::Point(0, 0);
			this->panel1->Name = L"panel1";
			this->panel1->Size = System::Drawing::Size(3840, 2160);
			this->panel1->TabIndex = 0;
			this->panel1->Paint += gcnew System::Windows::Forms::PaintEventHandler(this, &Install::panel1_Paint);
			// 
			// label2
			// 
			this->label2->AutoSize = true;
			this->label2->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, static_cast<System::Drawing::FontStyle>((System::Drawing::FontStyle::Bold | System::Drawing::FontStyle::Italic)),
				System::Drawing::GraphicsUnit::Point, static_cast<System::Byte>(0)));
			this->label2->ForeColor = System::Drawing::Color::Red;
			this->label2->Location = System::Drawing::Point(41, 611);
			this->label2->Name = L"label2";
			this->label2->Size = System::Drawing::Size(1037, 20);
			this->label2->TabIndex = 19;
			this->label2->Text = L"Note: Once you click a button, a Powershell window will open. To check the instal"
				L"l progress you may open that powershell window";
			// 
			// button13
			// 
			this->button13->BackColor = System::Drawing::Color::Indigo;
			this->button13->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button13->ForeColor = System::Drawing::SystemColors::ActiveCaption;
			this->button13->Location = System::Drawing::Point(726, 467);
			this->button13->Name = L"button13";
			this->button13->Size = System::Drawing::Size(178, 76);
			this->button13->TabIndex = 18;
			this->button13->Text = L"Adobe Acrobat Reader";
			this->button13->UseVisualStyleBackColor = false;
			this->button13->Click += gcnew System::EventHandler(this, &Install::button13_Click);
			// 
			// button12
			// 
			this->button12->BackColor = System::Drawing::Color::Indigo;
			this->button12->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button12->ForeColor = System::Drawing::SystemColors::ActiveCaption;
			this->button12->Location = System::Drawing::Point(726, 373);
			this->button12->Name = L"button12";
			this->button12->Size = System::Drawing::Size(178, 76);
			this->button12->TabIndex = 17;
			this->button12->Text = L"VLC Media Player";
			this->button12->UseVisualStyleBackColor = false;
			this->button12->Click += gcnew System::EventHandler(this, &Install::button12_Click);
			// 
			// button11
			// 
			this->button11->BackColor = System::Drawing::Color::Indigo;
			this->button11->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button11->ForeColor = System::Drawing::SystemColors::ActiveCaption;
			this->button11->Location = System::Drawing::Point(726, 271);
			this->button11->Name = L"button11";
			this->button11->Size = System::Drawing::Size(178, 76);
			this->button11->TabIndex = 16;
			this->button11->Text = L"Brave Browser";
			this->button11->UseVisualStyleBackColor = false;
			this->button11->Click += gcnew System::EventHandler(this, &Install::button11_Click);
			// 
			// button10
			// 
			this->button10->BackColor = System::Drawing::Color::Indigo;
			this->button10->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button10->ForeColor = System::Drawing::SystemColors::ActiveCaption;
			this->button10->Location = System::Drawing::Point(726, 168);
			this->button10->Name = L"button10";
			this->button10->Size = System::Drawing::Size(178, 76);
			this->button10->TabIndex = 15;
			this->button10->Text = L"OBS Studio";
			this->button10->UseVisualStyleBackColor = false;
			this->button10->Click += gcnew System::EventHandler(this, &Install::button10_Click);
			// 
			// button9
			// 
			this->button9->BackColor = System::Drawing::Color::Indigo;
			this->button9->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button9->ForeColor = System::Drawing::SystemColors::ActiveCaption;
			this->button9->Location = System::Drawing::Point(522, 467);
			this->button9->Name = L"button9";
			this->button9->Size = System::Drawing::Size(178, 76);
			this->button9->TabIndex = 14;
			this->button9->Text = L"Epic Games Launcher";
			this->button9->UseVisualStyleBackColor = false;
			this->button9->Click += gcnew System::EventHandler(this, &Install::button9_Click);
			// 
			// button8
			// 
			this->button8->BackColor = System::Drawing::Color::Indigo;
			this->button8->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button8->ForeColor = System::Drawing::SystemColors::ActiveCaption;
			this->button8->Location = System::Drawing::Point(522, 373);
			this->button8->Name = L"button8";
			this->button8->Size = System::Drawing::Size(178, 76);
			this->button8->TabIndex = 13;
			this->button8->Text = L"Steam";
			this->button8->UseVisualStyleBackColor = false;
			this->button8->Click += gcnew System::EventHandler(this, &Install::button8_Click);
			// 
			// button7
			// 
			this->button7->BackColor = System::Drawing::Color::Indigo;
			this->button7->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button7->ForeColor = System::Drawing::SystemColors::ActiveCaption;
			this->button7->Location = System::Drawing::Point(522, 271);
			this->button7->Name = L"button7";
			this->button7->Size = System::Drawing::Size(178, 76);
			this->button7->TabIndex = 12;
			this->button7->Text = L"Discord";
			this->button7->UseVisualStyleBackColor = false;
			this->button7->Click += gcnew System::EventHandler(this, &Install::button7_Click);
			// 
			// button6
			// 
			this->button6->BackColor = System::Drawing::Color::Indigo;
			this->button6->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button6->ForeColor = System::Drawing::SystemColors::ActiveCaption;
			this->button6->Location = System::Drawing::Point(522, 168);
			this->button6->Name = L"button6";
			this->button6->Size = System::Drawing::Size(178, 76);
			this->button6->TabIndex = 11;
			this->button6->Text = L"Chrome";
			this->button6->UseVisualStyleBackColor = false;
			this->button6->Click += gcnew System::EventHandler(this, &Install::button6_Click);
			// 
			// button5
			// 
			this->button5->BackColor = System::Drawing::Color::Indigo;
			this->button5->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button5->ForeColor = System::Drawing::SystemColors::ActiveCaption;
			this->button5->Location = System::Drawing::Point(318, 467);
			this->button5->Name = L"button5";
			this->button5->Size = System::Drawing::Size(178, 76);
			this->button5->TabIndex = 10;
			this->button5->Text = L"Spotify";
			this->button5->UseVisualStyleBackColor = false;
			this->button5->Click += gcnew System::EventHandler(this, &Install::button5_Click);
			// 
			// panel2
			// 
			this->panel2->AccessibleName = L"";
			this->panel2->AutoSize = true;
			this->panel2->BackColor = System::Drawing::Color::FromArgb(static_cast<System::Int32>(static_cast<System::Byte>(128)), static_cast<System::Int32>(static_cast<System::Byte>(255)),
				static_cast<System::Int32>(static_cast<System::Byte>(128)));
			this->panel2->Controls->Add(this->label1);
			this->panel2->Location = System::Drawing::Point(259, 0);
			this->panel2->Name = L"panel2";
			this->panel2->Size = System::Drawing::Size(3840, 88);
			this->panel2->TabIndex = 9;
			this->panel2->Paint += gcnew System::Windows::Forms::PaintEventHandler(this, &Install::panel2_Paint);
			// 
			// label1
			// 
			this->label1->AutoSize = true;
			this->label1->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 21.75F, static_cast<System::Drawing::FontStyle>((System::Drawing::FontStyle::Bold | System::Drawing::FontStyle::Italic)),
				System::Drawing::GraphicsUnit::Point, static_cast<System::Byte>(0)));
			this->label1->ForeColor = System::Drawing::Color::Red;
			this->label1->Location = System::Drawing::Point(3, 25);
			this->label1->Name = L"label1";
			this->label1->Size = System::Drawing::Size(178, 33);
			this->label1->TabIndex = 0;
			this->label1->Text = L"Install Apps";
			this->label1->TextAlign = System::Drawing::ContentAlignment::MiddleRight;
			// 
			// button4
			// 
			this->button4->BackColor = System::Drawing::Color::Indigo;
			this->button4->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button4->ForeColor = System::Drawing::SystemColors::ActiveCaption;
			this->button4->Location = System::Drawing::Point(318, 373);
			this->button4->Name = L"button4";
			this->button4->Size = System::Drawing::Size(178, 76);
			this->button4->TabIndex = 8;
			this->button4->Text = L"VSCode";
			this->button4->UseVisualStyleBackColor = false;
			this->button4->Click += gcnew System::EventHandler(this, &Install::button4_Click);
			// 
			// button3
			// 
			this->button3->BackColor = System::Drawing::SystemColors::ActiveCaptionText;
			this->button3->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button3->ForeColor = System::Drawing::SystemColors::ActiveCaption;
			this->button3->Location = System::Drawing::Point(1831, 1042);
			this->button3->Name = L"button3";
			this->button3->Size = System::Drawing::Size(178, 76);
			this->button3->TabIndex = 7;
			this->button3->Text = L"Notepad++";
			this->button3->UseVisualStyleBackColor = false;
			// 
			// button1
			// 
			this->button1->BackColor = System::Drawing::Color::Indigo;
			this->button1->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button1->ForeColor = System::Drawing::SystemColors::ActiveCaption;
			this->button1->Location = System::Drawing::Point(318, 271);
			this->button1->Name = L"button1";
			this->button1->Size = System::Drawing::Size(178, 76);
			this->button1->TabIndex = 6;
			this->button1->Text = L"Notepad++";
			this->button1->UseVisualStyleBackColor = false;
			this->button1->Click += gcnew System::EventHandler(this, &Install::button1_Click);
			// 
			// button2
			// 
			this->button2->BackColor = System::Drawing::Color::Indigo;
			this->button2->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 12, System::Drawing::FontStyle::Bold, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->button2->ForeColor = System::Drawing::SystemColors::ActiveCaption;
			this->button2->Location = System::Drawing::Point(318, 168);
			this->button2->Name = L"button2";
			this->button2->Size = System::Drawing::Size(178, 76);
			this->button2->TabIndex = 5;
			this->button2->Text = L"Firefox";
			this->button2->UseVisualStyleBackColor = false;
			this->button2->Click += gcnew System::EventHandler(this, &Install::button2_Click);
			// 
			// pictureBox1
			// 
			this->pictureBox1->BackgroundImage = (cli::safe_cast<System::Drawing::Image^>(resources->GetObject(L"pictureBox1.BackgroundImage")));
			this->pictureBox1->BackgroundImageLayout = System::Windows::Forms::ImageLayout::Stretch;
			this->pictureBox1->Location = System::Drawing::Point(0, 0);
			this->pictureBox1->Name = L"pictureBox1";
			this->pictureBox1->Size = System::Drawing::Size(260, 89);
			this->pictureBox1->TabIndex = 4;
			this->pictureBox1->TabStop = false;
			this->pictureBox1->Click += gcnew System::EventHandler(this, &Install::pictureBox1_Click);
			// 
			// Install
			// 
			this->AutoScaleDimensions = System::Drawing::SizeF(6, 13);
			this->AutoScaleMode = System::Windows::Forms::AutoScaleMode::Font;
			this->ClientSize = System::Drawing::Size(1264, 681);
			this->Controls->Add(this->panel1);
			this->Icon = (cli::safe_cast<System::Drawing::Icon^>(resources->GetObject(L"$this.Icon")));
			this->MaximizeBox = false;
			this->MinimumSize = System::Drawing::Size(800, 600);
			this->Name = L"Install";
			this->Text = L"Install Apps";
			this->panel1->ResumeLayout(false);
			this->panel1->PerformLayout();
			this->panel2->ResumeLayout(false);
			this->panel2->PerformLayout();
			(cli::safe_cast<System::ComponentModel::ISupportInitialize^>(this->pictureBox1))->EndInit();
			this->ResumeLayout(false);

		}
#pragma endregion
	private: System::Void panel1_Paint(System::Object^ sender, System::Windows::Forms::PaintEventArgs^ e) {
	}
	private: System::Void button2_Click(System::Object^ sender, System::EventArgs^ e) {
		system("start powershell.exe winget install Mozilla.Firefox -e");
	}
	private: System::Void button1_Click(System::Object^ sender, System::EventArgs^ e) {
		system("start powershell.exe winget install Notepad++.Notepad++ -e");
	}
private: System::Void button4_Click(System::Object^ sender, System::EventArgs^ e) {
		system("start powershell.exe winget install Microsoft.VisualStudioCode -e");
}
private: System::Void panel2_Paint(System::Object^ sender, System::Windows::Forms::PaintEventArgs^ e) {
}
private: System::Void pictureBox1_Click(System::Object^ sender, System::EventArgs^ e) {
}
private: System::Void button6_Click(System::Object^ sender, System::EventArgs^ e) {
		system("start powershell.exe winget install Google.Chrome -e");
}
private: System::Void button7_Click(System::Object^ sender, System::EventArgs^ e) {
		system("start powershell.exe winget install Discord.Discord -e");
}
private: System::Void button5_Click(System::Object^ sender, System::EventArgs^ e) {
		system("start powershell.exe winget install Spotify.Spotify -e");
}
private: System::Void button8_Click(System::Object^ sender, System::EventArgs^ e) {
		system("start powershell.exe winget install Valve.Steam -e");
}
private: System::Void button9_Click(System::Object^ sender, System::EventArgs^ e) {
		system("start powershell.exe winget install EpicGames.EpicGamesLauncher -e");
}
private: System::Void button10_Click(System::Object^ sender, System::EventArgs^ e) {
		system("start powershell.exe winget install OBSProject.OBSStudio -e");
}
private: System::Void button11_Click(System::Object^ sender, System::EventArgs^ e) {
		system("start powershell.exe winget install BraveSoftware.BraveBrowser -e");
}
private: System::Void button12_Click(System::Object^ sender, System::EventArgs^ e) {
		system("start powershell.exe winget install VideoLAN.VLC -e");
}
private: System::Void button13_Click(System::Object^ sender, System::EventArgs^ e) {
		system("start powershell.exe winget install Adobe.Acrobat.Reader.64-bit -e");
}
};
}
