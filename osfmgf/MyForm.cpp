#include "MyForm.h"
#include "Install.h"
using namespace System;

using namespace System::Windows::Forms;

[STAThread]

void main(array<String^>^ args)

{

    Application::EnableVisualStyles();

    Application::SetCompatibleTextRenderingDefault(false);

    osfmgf::MyForm form;

    Application::Run(% form);

}